*******************************************
Radial and Axial Expansion and Contraction
*******************************************

ARMI natively supports both one-dimensional radial and axial expansion. These expansion types function independently of one another and each have their own set of underlying assumptions and use-cases. In the following sections we describe their design, limitations, and intended functionality.

Thermal Expansion
-----------------
ARMI treats thermal expansion as a linear phenomena using the standard linear expansion relationship,

.. math::
    :linearExp:
    \frac{\Delta L}{L_0} = \alpha \Delta T,

where, :math:`\Delta L` and :math:`\Delta T` are the change in length and temperature from the reference state, respectively, and :math:`\alpha` is the thermal expansion coefficient. 

.. math::
    :label: diffEq
    \frac{dL}{dT} = \alpha T

Equation :eq:`diffEq` does stuff.

Radial Expansion
----------------
In ARMI, radial expansion occurs at the component level. However, radial expansion does not actually affect the geometry of the components. Rather, radial "expansion" occurs when the dimensions of a component are queried via :py:meth:`getDimension <armi.reactor.components.component.Component.getDimension>`. 

Component to component linking is described in Section :ref:`componentLinks`. 

The delta between the temperature, Tc (which is typically c.temperatureInC), then generates a thermal expansion factor that modifies the returned dimension - which in turn affects the value that gets returned if you query quantities that depend on dimension.

Axial Expansion
---------------
