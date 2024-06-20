*********************************
Thermal Expansion and Contraction
*********************************

ARMI natively supports linear expansion in both the radial and axial dimensions. These expansion types function 
independently of one another and each have their own set of underlying assumptions and use-cases. The remainder of this 
section is described as follows: in Section :ref:`thermalExpansion` the methodology used for thermal expansion within 
ARMI is described; in Sections :ref:`radialExpansion` and :ref:`axialExpansion`, we describe the design, limitations, 
and intended functionality of radial and axial expansion, respectively.

.. _thermalExpansion:

Thermal Expansion
=================
ARMI treats thermal expansion as a linear phenomena using the standard linear expansion relationship,

.. math::
    \frac{\Delta L}{L_0} = \alpha(T) \Delta T,
    :label: linearExp

where, :math:`\Delta L` and :math:`\Delta T` are the change in length and temperature from the reference state, 
respectively, and :math:`\alpha` is the thermal expansion coefficient relative to :math:`T_0`. Expanding and rearranging
Equation :eq:`linearExp`, we can obtain an expression for the new length, :math:`L_1`,

.. math::
    L_1 = L_0\left[1 + \alpha(T_1)\left(T_1 - T_0\right) \right].
    :label: newLength

Given Equation :eq:`linearExp`, we can create expressions for the change in length between our "hot" 
temperature (Equation :eq:`hotExp`)

.. math::
    \begin{aligned}
        \frac{L_h - L_0}{L_0} &= \alpha(T_h)\left(T_h - T_0\right),\\
        \frac{L_h}{L_0} &= 1 + \alpha(T_h)\left(T_h - T_0\right).
    \end{aligned}
    :label: hotExp

and "non-reference" temperature, :math:`T_c` (Equation :eq:`nonRefExp`),

.. math::
    \begin{aligned}
        \frac{L_c - L_0}{L_0} &= \alpha(T_c)\left(T_c - T_0\right),\\
        \frac{L_c}{L_0} &= 1 + \alpha(T_c)\left(T_c - T_0\right).
    \end{aligned}
    :label: nonRefExp

These are used within ARMI to enable thermal expansion and contraction with a temperature not equal to the reference 
temperature, :math:`T_0`. By taking the difference between Equation :eq:`hotExp` and :eq:`nonRefExp`, we can obtain an 
expression relating the change in length, :math:`L_h - L_c`, to the reference length, :math:`L_0`,

.. math::
    \begin{aligned}
        \frac{L_h - L_0}{L_0} - \frac{L_c - L_0}{L_0} &= \frac{L_h}{L_0} - 1 - \frac{L_c}{L_0} + 1, \\
        &= \frac{L_h - L_c}{L_0}.
    \end{aligned}
    :label: diffHotNonRef

Using Equations :eq:`diffHotNonRef` and :eq:`nonRefExp`, we can obtain an expression for the change in length, 
:math:`L_h - L_c`, relative to the non-reference temperature,

.. math::
    \frac{L_h - L_c}{L_c} &= \frac{L_h - L_c}{L_0} \frac{L_0}{L_c}\\
    &= \left( \frac{L_h}{L_0} - \frac{L_c}{L_0} \right) \left( 1 + \alpha(T_c)\left(T_c - T_0\right) \right)^{-1}.
    :label: expNewRelative

Using Equations :eq:`hotExp` and :eq:`nonRefExp`, we can simplify Equation :eq:`expNewRelative` to find,

.. math::
    \frac{L_h - L_c}{L_c} = \frac{\alpha(T_h) \left(T_h - T_0\right) - \alpha(T_c)\left(T_c - T_0\right)}{1 + \alpha(T_c)\left(T_c - T_0\right)}.
    :label: linearExpansionFactor

Equation :eq:`linearExpansionFactor` is the expression used by ARMI in 
:py:meth:`linearExpansionFactor <armi.materials.material.Material.linearExpansionFactor>` and is used to thermally 
expand ARMI Components. 

.. note::
    :py:meth:`linearExpansionPercent <armi.materials.material.Material.linearExpansionPercent>` returns 
    :math:`\frac{L - L_0}{L_0}` in %.

***************
Axial Expansion
***************

Within ARMI, axial expansion is performed at the Component-level for a given Assembly through the 
:py:class:`axialExpansionChanger <armi.reactor.converters.axialExpansionChanger.AxialExpansionChanger>`. The 
recognized assumptions and limitations are as follows:

1. Axial expansion is only supported for pin-type Assemblies and is done Assembly-by-Assembly.
2. Axial expansion only occurs for solid materials.
    * Assembly coolant is assumed to be a :py:meth:`DerivedShape <armi.reactor.components.DerivedShape>` and whose
      volume is recomputed based on the expansion of the neighboring solid materials.
    * Axial expansion of other fluid-based materials is neglected at this time. 

At a high level, axial expansion within ARMI occurs in three steps: 

1. Determine axial linkage of Components between axially neighboring Blocks.
2. Assign expansion factors to each solid Component. 
    * Expansion factors are typically computed thermal expansion factors via
      :py:meth:`computeThermalExpansionFactors <armi.reactor.converters.axialExpansionChanger.ExpansionData.computeThermalExpansionFactors>`.
      However, predetermined expansion factors may be directly assigned to Components via
      :py:meth:`setExpansionFactors <armi.reactor.converters.axialExpansionChanger.ExpansionData.setExpansionFactors>`.
3. Perform axial expansion.

Steps 1 and 3 are described in Sections :ref:`axialLinkage` and :ref:`axialExp`, respectively. Section 
:ref:`thermalExpansion` describes how thermal expansion coefficients are calculated and :ref:`assigningExpFactors` 
describes the different use cases and how to perform prescribed expansion. 

.. _axialLinkage:

Determining Component Axial Linkage
===================================

Prior to performing any expansion, the axial expansion functionality needs to understand the axial linkage of 
Components between axially neighboring blocks. This is critical to preserving physical realism of axial expansion. 
For example, consider the case of three axially neighboring blocks shown in Figure ABC_1.

.. show figure with two prototypical Sodium-cooled fast reactor blocks and a Plenum Block
.. this is essentially a piece of the detailedAxialExpansion test reactor

To properly preserve reactivity feedback phenomena resulting from axial expansion, the fuel in the lower Block needs to 
physically *push up* on the fuel pin above it pushing it into the Plenum Block. (analogously, the clad and duct need to 
have similar movement). To accomplish this, the axial expansion changer performs the following:

1. For a given Block, `B0`, determine the blocks that are axially linked to it by comparing the lower and upper bounds.
2. For each solid component within `B0`, compare the solid components within each linked Block to determine if the 
   solid components are linked. This determination is completed in the following manner:
    - The two components must be the same type (e.g.,
    :py:class:`Circle <armi.reactor.components.basicShapes.Circle>`,
    :py:class:`Hexagon <armi.reactor.components.basicShapes.Hexagon>`, etc).
    - The two components must have the same multiplicity.
    - The two components must have geometrically overlap. This metric is quantied by computing the inner and outer
      "diameter" of each component and checking to see if either component can fit within the other. The inner and 
      outer "diameter" of each component is measured via the specific shape subclass implementation of
      :py:meth:`getCircleInnerDiameter <armi.reactor.components.component.Component.getCircleInnerDiameter>`and 
      :py:meth:`getBoundingCircleOuterDiameter <armi.reactor.components.component.Component.getBoundingCircleOuterDiameter>`
      , respectively. **add a figure here showing some examples of what this looks like**

During the determination of axial linkage, there is one user-facing warning and one fatal error. The warning is in 
regard to :py:class:`UnshapedComponent <armi.reactor.components.UnshapedComponent>`. These types of components are 
idealized constructs that have no formal shape and therefore explictly axially linking them for axial expansion is 
unphysical. The error is raised if a given component is found to be axially linked to multiple components. This is 
typically indicative of an error in the blueprints and occurs when there is overlap between multiple components. 
Support for such designs may included in the future. 

.. _assigningExpFactors:

Assigning Expansion Factors to Each Component
=============================================

- connect this to the thermal expansion methodology
- describe the different use cases and options for thermal expansion
- describe the prescribed expansion option 


.. _axialExp:

Axial Expansion Mechanics in ARMI
=================================

**show figure here of two blocks expanding and the lower pushing up on the upper with uniform expansion**



Using the `igniter fuel` Assembly from the test reactor blueprints provided in 
`armi.tests.detailedAxialExpansion.refSmallReactorBase`, we can illustrate the logic used to determine axial linkage. 




Non-Uniform Expansion
=====================

In ARMI, axial linkage of the components 

Figure XYZ above shows the simple case of uniform expansion. However, ind reality, each solid material may expand at 
different rates due to varying material composition and/or temperatures. To accomodate this, the concept of a 
"dummy" Block is introduced. The purpose of the dummy block is to allow 

Control Assembly Expansion and Contraction
==========================================

Assumptions and limitations of axial expansion for control assemblies is discussed in Section ABC.

..
.. OUTLINE 
..
.. Thermal Expansion 
.. -----------------
.. 1. Show thermal expansion equations. (done in doc/user/radial_and_thermal_expansion.rst)

.. Axial Expansion Outline
.. -----------------------
.. 2. Describe how axial expansion occurs in an assembly. 
..    - Component-wise expansion -> axial expansion target component -> how this 
..      gets used to redraw block boundaries.
..    - Drop a note for how prescribed expansion comes into play with the equations.
..    - Appendix for control assemblies. Discuss how it does not account for
..        CRDL expansion nor downward expansion. Provide the underlying assumption
..        of how the pin bundle expansion should be used. 
.. 3. Describe how to obtain mass conservation in axial expansion. Show cases where 
..    it is lost and how to obtain it. 
.. 4. Leave documentation connecting Assembly-based expansion to the uniform mesh
..    converter. I.e., say that after looping over every Assembly in a given Core, 
..    you'll have an axially disjoint Core that (likely) needs to be unified.  

.. Radial Expansion Outline
.. ------------------------
.. 1. Discuss Component-based radial expansion and how radial component linking works.