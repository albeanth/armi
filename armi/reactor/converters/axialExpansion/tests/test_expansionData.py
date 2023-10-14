import unittest
from numpy import zeros

from armi.reactor.flags import Flags
from armi.reactor.blocks import HexBlock
from armi.reactor.components import DerivedShape
from armi.reactor.components.basicShapes import Circle, Hexagon
from armi.reactor.converters.axialExpansion.expansionData import ExpansionData
from armi.reactor.converters.axialExpansion.tests.buildAxialExpAssembly import (
    buildTestAssembly,
)


class TestSetExpansionFactors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = buildTestAssembly("HT9")
        cls.expData = ExpansionData(cls.a, False, False)

    def test_setExpansionFactors(self):
        cList = self.a[0].getChildren()
        expansionGrowthFracs = range(1, len(cList) + 1)
        self.expData.setExpansionFactors(cList, expansionGrowthFracs)
        for c, expFrac in zip(cList, expansionGrowthFracs):
            self.assertEqual(self.expData._expansionFactors[c], expFrac)

    def test_setExpansionFactors_Exceptions(self):
        with self.assertRaises(RuntimeError) as cm:
            cList = self.a[0].getChildren()
            expansionGrowthFracs = range(len(cList) + 1)
            self.expData.setExpansionFactors(cList, expansionGrowthFracs)
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code, 3)

        with self.assertRaises(RuntimeError) as cm:
            cList = self.a[0].getChildren()
            expansionGrowthFracs = zeros(len(cList))
            self.expData.setExpansionFactors(cList, expansionGrowthFracs)
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code, 3)

        with self.assertRaises(RuntimeError) as cm:
            cList = self.a[0].getChildren()
            expansionGrowthFracs = zeros(len(cList)) - 10.0
            self.expData.setExpansionFactors(cList, expansionGrowthFracs)
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code, 3)


class TestDetermineTargetComponent(unittest.TestCase):
    """Verify determineTargetComponent method is properly updating _componentDeterminesBlockHeight."""

    def setUp(self):
        self.expData = ExpansionData([], setFuel=True, expandFromTinputToThot=True)
        coolDims = {"Tinput": 25.0, "Thot": 25.0}
        self.coolant = DerivedShape("coolant", "Sodium", **coolDims)

    def test_determineTargetComponent(self):
        """Provides coverage for searching TARGET_FLAGS_IN_PREFERRED_ORDER."""
        b = HexBlock("fuel", height=10.0)
        fuelDims = {"Tinput": 25.0, "Thot": 25.0, "od": 0.76, "id": 0.00, "mult": 127.0}
        cladDims = {"Tinput": 25.0, "Thot": 25.0, "od": 0.80, "id": 0.77, "mult": 127.0}
        fuel = Circle("fuel", "HT9", **fuelDims)
        clad = Circle("clad", "HT9", **cladDims)
        b.add(fuel)
        b.add(clad)
        b.add(self.coolant)
        # make sure that b.p.axialExpTargetComponent is empty initially
        self.assertFalse(b.p.axialExpTargetComponent)
        # call method, and check that target component is correct
        self.expData.determineTargetComponent(b)
        self.assertTrue(
            self.expData.isTargetComponent(fuel),
            msg=f"determineTargetComponent failed to recognize intended component: {fuel}",
        )
        self.assertEqual(
            b.p.axialExpTargetComponent,
            fuel.name,
            msg=f"determineTargetComponent failed to recognize intended component: {fuel}",
        )

    def test_determineTargetComponentBlockWithMultipleFlags(self):
        """Provides coverage for searching TARGET_FLAGS_IN_PREFERRED_ORDER with multiple flags."""
        # build a block that has two flags as well as a component matching each
        b = HexBlock("fuel poison", height=10.0)
        fuelDims = {"Tinput": 25.0, "Thot": 25.0, "od": 0.9, "id": 0.5, "mult": 200.0}
        poisonDims = {"Tinput": 25.0, "Thot": 25.0, "od": 0.5, "id": 0.0, "mult": 10.0}
        fuel = Circle("fuel", "HT9", **fuelDims)
        poison = Circle("poison", "HT9", **poisonDims)
        b.add(fuel)
        b.add(poison)
        b.add(self.coolant)
        # call method, and check that target component is correct
        self.expData.determineTargetComponent(b)
        self.assertTrue(
            self.expData.isTargetComponent(fuel),
            msg=f"determineTargetComponent failed to recognize intended component: {fuel}",
        )

    def test_specifyTargetComponent_NotFound(self):
        """Ensure RuntimeError gets raised when no target component is found."""
        b = HexBlock("fuel", height=10.0)
        b.add(self.coolant)
        b.setType("fuel")
        with self.assertRaises(RuntimeError) as cm:
            self.expData.determineTargetComponent(b)
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code, 3)
        with self.assertRaises(RuntimeError) as cm:
            self.expData.determineTargetComponent(b, Flags.FUEL)
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code, 3)

    def test_specifyTargetComponent_singleSolid(self):
        """Ensures that specifyTargetComponent is smart enough to set the only solid as the target component."""
        b = HexBlock("plenum", height=10.0)
        ductDims = {"Tinput": 25.0, "Thot": 25.0, "op": 17, "ip": 0.0, "mult": 1.0}
        duct = Hexagon("duct", "HT9", **ductDims)
        b.add(duct)
        b.add(self.coolant)
        b.getVolumeFractions()
        b.setType("plenum")
        self.expData.determineTargetComponent(b)
        self.assertTrue(
            self.expData.isTargetComponent(duct),
            msg=f"determineTargetComponent failed to recognize intended component: {duct}",
        )

    def test_specifyTargetComponet_MultipleFound(self):
        """Ensure RuntimeError is hit when multiple target components are found.

        Notes
        -----
        This can occur if a block has a mixture of fuel types. E.g., different fuel materials,
        or different fuel geometries.
        """
        b = HexBlock("fuel", height=10.0)
        fuelAnnularDims = {
            "Tinput": 25.0,
            "Thot": 25.0,
            "od": 0.9,
            "id": 0.5,
            "mult": 100.0,
        }
        fuelDims = {"Tinput": 25.0, "Thot": 25.0, "od": 1.0, "id": 0.0, "mult": 10.0}
        fuel = Circle("fuel", "HT9", **fuelDims)
        fuelAnnular = Circle("fuel annular", "HT9", **fuelAnnularDims)
        b.add(fuel)
        b.add(fuelAnnular)
        b.add(self.coolant)
        b.setType("FuelBlock")
        with self.assertRaises(RuntimeError) as cm:
            self.expData.determineTargetComponent(b, flagOfInterest=Flags.FUEL)
            the_exception = cm.exception
            self.assertEqual(the_exception.error_code, 3)

    def test_manuallySetTargetComponent(self):
        """Ensures that target components can be manually set (is done in practice via blueprints)."""
        b = HexBlock("dummy", height=10.0)
        ductDims = {"Tinput": 25.0, "Thot": 25.0, "op": 17, "ip": 0.0, "mult": 1.0}
        duct = Hexagon("duct", "HT9", **ductDims)
        b.add(duct)
        b.add(self.coolant)
        b.getVolumeFractions()
        b.setType("duct")

        # manually set target component
        b.setAxialExpTargetComp(duct)
        self.assertEqual(
            b.p.axialExpTargetComponent,
            duct.name,
        )

        # check that target component is stored on expansionData object correctly
        self.expData._componentDeterminesBlockHeight[
            b.getComponentByName(b.p.axialExpTargetComponent)
        ] = True
        self.assertTrue(self.expData.isTargetComponent(duct))
