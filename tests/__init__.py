import unittest
import tests.efsc.test_efsc_tools
import tests.efsm.test_efsm_tools
import tests.efsb.test_efsb_tools

def efst_test_suite():

    loader = unittest.TestLoader()

    # load tests from the efsc package
    efsc_tools_suite = loader.loadTestsFromModule(tests.efsc.test_efsc_tools)

    # load tests from the efsm package
    efsm_tools_suite = loader.loadTestsFromModule(tests.efsm.test_efsm_tools)

    # load tests from the efsm package
    efsb_tools_suite = loader.loadTestsFromModule(tests.efsb.test_efsb_tools)



    # add all tests to EFST suite
    efst_test_suite = unittest.TestSuite()
    efst_test_suite.addTests(efsc_tools_suite)
    efst_test_suite.addTests(efsm_tools_suite)
    efst_test_suite.addTests(efsb_tools_suite)

    return efst_test_suite
