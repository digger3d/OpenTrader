# -*-mode: python; py-indent-offset: 4; indent-tabs-mode: nil; encoding: utf-8-dos; coding: utf-8 -*-

"""
"""

import sys
import os
import collections
from pybacktest.data import load_from_yahoo

#? feed rename delete
sBAC__doc__ = ""
sBACfeed__doc__ = """
back feed dir
back feed dir dirname

back feed read_mt4_csv SYMBOL TIMEFRAME [YEAR] - read a CSV file from Mt4
back feed read_yahoo_csv SYMBOL [STARTYEAR]
back feed list                                 - list the feeds we have read
back feed get                                  - get the key name of the current feed
back feed info
back feed plot
"""
sBAC__doc__ += sBACfeed__doc__

sBACrecipe__doc__ = """
back recipe list                                 - list the known recipes
back recipe set                                  - show the current recipe
back recipe set RECIPE                           - set the current recipe
back recipe ingredients                          - make the ingredients
"""
sBAC__doc__ += sBACrecipe__doc__

sBACchef__doc__ = """
back chef list                          - list the known chefs
back chef set                           - show the current chef
back chef set CHEF                      - set the current chef
back chef cook                          - cook the recipe by the chef
"""
sBAC__doc__ += sBACchef__doc__

sBACservings__doc__ = """
back servings list                               - list the servings
back servings signals
back servings trades
back servings positions
back servings equity
back servings summary
"""
sBAC__doc__ += sBACservings__doc__

sBACplot__doc__ = """
back plot show
back plot set
back plot trades
back plot equity
"""
sBAC__doc__ += sBACplot__doc__

dRunCache = {}

global dFEED_CACHE
dFEED_CACHE = {}
global sFEED_CACHE_KEY
sFEED_CACHE_KEY = ""

_sCurrentOmletteDir = ""
_oCurrentOmlette = None
_oCurrentRecipe = None
_oCurrentChef = None

def oEnsureOmlette(self, oOpts, sNewOmlette=""):
    from Omlettes import Omlette
    if not sNewOmlette and hasattr(self, 'oOm') and \
       self.oOm:
        return self.oOm
    if not sNewOmlette:
        # The default is no HDF file - it's not in self.oOptions.sOmlette
        pass
    oOm = Omlette.Omlette(sHdfStore=sNewOmlette, oFd=sys.stdout)
    self.oOm = oOm
    return oOm

def oEnsureRecipe(self, oOpts, sNewRecipe=""):
    oOm = oEnsureOmlette(self, oOpts)
    if not sNewRecipe and hasattr(oOm, 'oRecipe') and oOm.oRecipe:
        return oOm.oRecipe
    if not sNewRecipe:
        # The are set earlier in the call to do_back
        sNewRecipe = self.sRecipe
    if hasattr(oOm, 'oRecipe') and oOm.oRecipe:
        sOldName = oOm.oRecipe.sName
    else:
        sOldName = ""
    oRecipe = oOm.oAddRecipe(sNewRecipe)
    if sOldName and sOldName != sNewRecipe:        
        #? do we invalidate the current servings if the recipe changed?
        vClearOven(self, oOpts)
    return oOm.oRecipe

def oEnsureChef(self, oOpts, sNewChef=""):
    oOm = oEnsureOmlette(self, oOpts)
    if not sNewChef and hasattr(oOm, 'oChefModule') and oOm.oChefModule:
        return oOm.oChefModule
    if not sNewChef:
        # The are set earlier in the call to do_back
        sNewChef = self.sChef
    if hasattr(oOm, 'oChefModule') and oOm.oChefModule and oOm.oChefModule.sChef:
        sOldName = oOm.oChefModule.sChef
    else:
        sOldName = ""
    oChefModule = oOm.oAddChef(sNewChef)
    if sOldName and sOldName != sNewChef:
	#? do we invalidate the current servings if the chef changed?
        vClearOven(self, oOpts)
    return oOm.oChefModule

def vClearOven(self, oOpts):
    oOm = oEnsureOmlette(self, oOpts)
    oOm.oBt = None
    
def vDoBacktestCmd(self, oArgs, oOpts=None):
    __doc__ = sBAC__doc__
    global dFEED_CACHE
    global sFEED_CACHE_KEY

    # begin end
    _sCurrentFeedDir = '/t/Program Files/HotForex MetaTrader/history/tools.fxdd.com'

    lArgs = oArgs.split()
    if lArgs[0] == 'omlette':
        global _sCurrentOmletteDir
        # ingredients recipe dish
        _lCmds = ['load', 'check', 'save', 'display']
        assert len(lArgs) > 1, "ERROR: " +lArgs[0] +" " +str(_lCmds)
        assert lArgs[1] in _lCmds, "ERROR: " +lArgs[0] +" " +str(_lCmds)
        if lArgs[1] == 'check':
            return
        if lArgs[1] == 'display':
            return
        assert len(lArgs) >= 3, \
               "ERROR: " +lArgs[0] +" " +lArgs[1] +" " +" filename"
        sFile = lArgs[2]
        if not os.path.exists(os.path.dirname(sFile)) and \
               os.path.exists(_sCurrentOmletteDir):
            # FixxME: check relative
            s = os.path.join(_sCurrentOmletteDir, sFile)
            if os.path.exists(s): sFile = s
        if lArgs[1] == 'load':
            assert os.path.isfile(sFile), \
                   "ERROR: " +lArgs[0] +" " +lArgs[1] +" file not found " +sFile
            _sCurrentOmletteDir = os.path.dirname(sFile)
            return
        if lArgs[1] == 'save':
            _sCurrentOmletteDir = os.path.dirname(sFile)
            return

        self.vError("Unrecognized omlette command: " + str(oArgs) +'\n' +__doc__)
        return

    if lArgs[0] == 'feed':
        __doc__ = sBACfeed__doc__
        #? rename delete
        _lCmds = ['dir', 'list', 'get', 'set',
                  'read_mt4_csv', 'read_yahoo_csv', 'info', 'plot', 'to_hdf']
        assert len(lArgs) > 1, "ERROR: " +lArgs[0] +" " +str(_lCmds)
        assert lArgs[1] in _lCmds, "ERROR: " +lArgs[0] +" " +str(_lCmds)

        
        if lArgs[1] == 'dir':
            if len(lArgs) == 2:
                if not _sCurrentFeedDir:
                    self.poutput("No default history directory set: use \"feed dir dir\"")
                else:
                    self.poutput("Default history directory: " + _sCurrentFeedDir)
                return
            sDir = lArgs[2]
            assert os.path.isdir(sDir)
            _sCurrentFeedDir = sDir
            return
        
        if lArgs[1] == 'read_mt4_csv':
            from OTBackTest import oReadMt4Csv
            assert len(lArgs) >= 3, \
                   "ERROR: " +lArgs[0] +" " +lArgs[1] +" FILENAME [SYMBOL TIMEFRAME YEAR]"
            sFile = lArgs[2]
            if not os.path.isfile(sFile):
                sHistoryDir = os.path.join(self.oOptions.sMt4Dir, 'history')
                assert os.path.isdir(sHistoryDir)
                import glob
                l = glob.glob(sHistoryDir +"/*/" +sFile)
                if l:
                    sFile = l[0]
                    self.vInfo("Found history file: " + sFile)
            assert os.path.isfile(sFile), \
                   "ERROR: " +lArgs[0] +" " +lArgs[1] +" file not found " +sFile
            if len(lArgs) > 5:
                sSymbol= lArgs[3]
                sTimeFrame = lArgs[4]
                sYear = lArgs[5]
            else:
                lCooked = os.path.split(sFile)[-1].split('.')[0].split('-')
                if len(lCooked) > 1:
                    sYear = lCooked[-1]
                else:
                    sYear = ""
                sSymbol = lCooked[0][:6]
                sTimeFrame = lCooked[0][6:]

            self.vDebug(lArgs[0] +" " +lArgs[1] +" " + \
                       "sSymbol=" +sSymbol \
                       +", sYear=" +sYear \
                       +", sTimeFrame=" +sTimeFrame)

            mFeedOhlc = oReadMt4Csv(sFile, sTimeFrame, sSymbol, sYear="")
            assert mFeedOhlc is not None, "oReadMt4Csv failed on " + sFile
            mFeedOhlc.info(True, sys.stdout)

            # NaturalNameWarning: object name is not a valid Python identifier: 'Mt4_csv|EURUSD|1440|2014'; it does not match the pattern ``^[a-zA-Z_][a-zA-Z0-9_]*$``;
            sKey = 'Mt4_csv' +'_' +sSymbol +'_' +sTimeFrame +'_' +sYear
            oOm = oEnsureOmlette(self, oOpts)
            _dCurrentFeedFrame = oOm.dGetFeedFrame(sFile,
                                                   sTimeFrame,
                                                   sSymbol,
                                                   sYear)
            from PandasMt4 import oReadMt4Csv, oPreprocessOhlc, vCookFiles
            mFeedOhlc = oPreprocessOhlc(_dCurrentFeedFrame['mFeedOhlc'])
            sys.stdout.write('INFO:  Data Open length: %d\n' % len(mFeedOhlc))
            _dCurrentFeedFrame['mFeedOhlc'] = mFeedOhlc
            
            dFEED_CACHE[sKey] = _dCurrentFeedFrame
            sFEED_CACHE_KEY = sKey
            return

        _lFeedCacheKeys = dFEED_CACHE.keys()
        if lArgs[1] == 'list':
            self.poutput("Feed keys: %r" % (self.G(_lFeedCacheKeys,)))
            return
        
        if lArgs[1] == 'get':
            self.poutput("Current Feed key: %s" % (self.G(sFEED_CACHE_KEY,)))
            return
        
        if lArgs[1] == 'set':
            assert len(lArgs) >= 3, \
                   "ERROR: " +lArgs[0] +" " +lArgs[1] +" " + '|'.join(_lFeedCacheKeys)
            sKey = lArgs[2]
            assert sKey in _lFeedCacheKeys, \
                   "ERROR: " +lArgs[0] +" " +lArgs[1] +" " + '|'.join(_lFeedCacheKeys)
            sFEED_CACHE_KEY = sKey
            return
        
        # The following all require that a feed has been loaded
        _dCurrentFeedFrame = dFEED_CACHE[sFEED_CACHE_KEY]

        if _dCurrentFeedFrame is None:
            self.vError("Run \"back read_*\" first to read a DataFrame")
            return
        sSymbol = _dCurrentFeedFrame['sSymbol']
        sKey = _dCurrentFeedFrame['sKey']
        sTimeFrame = _dCurrentFeedFrame['sTimeFrame']
        mFeedOhlc = _dCurrentFeedFrame['mFeedOhlc']

        if lArgs[1] in ['to_hdf']:
            """ DataFrame.to_hdf(path_or_buf, key, **kwargs)
            activate the HDFStore
            Parameters :
              path_or_buf : the path (string) or buffer to put the store
              key : string indentifier for the group in the store
              """

            assert len(lArgs) >= 3, \
                   "ERROR: " +lArgs[0] +" " +lArgs[1] +" fixed|table filename"
            sType = lArgs[2]
            assert sType in ['fixed', 'table']
            sFile = lArgs[3]
            # FixME: if absolute assert os.path.exists(os.path.dirname(sFile))
            #? lArgs[4:] -> **kw ?
            vRetval = mFeedOhlc.to_hdf(sFile, sKey, format=sType)
            return

        _dPlotParams = self.oConfig['feed.plot.params']

        if lArgs[1] == 'info':
            """ Concise summary of a DataFrame.
            Parameters :
            verbose : boolean, default True
                    If False, don’t print column count summary
            buf : writable buffer, defaults to sys.stdout
            """
            import yaml

            mFeedOhlc.info(True, sys.stdout)

            s = '|  %s  |' % ("Plot Params",)
            self.poutput('-' * len(s))
            self.poutput(s)
            self.poutput('-' * len(s))
            yaml.dump(_dPlotParams,
                      allow_unicode=True,
                      default_flow_style=False)
            self.poutput('-' * len(s))
            return

        # 'download_hst_zip'
        if lArgs[1] == 'plot':
            import matplotlib
            import numpy as np
            from PpnAmgcTut import vGraphData
            if 'matplotlib.rcParams' in self.oConfig:
                for sKey, gVal in self.oConfig['matplotlib.rcParams'].items():
                    matplotlib.rcParams[sKey] = gVal

            from OTBackTest import oPreprocessOhlc
            mFeedOhlc = oPreprocessOhlc(mFeedOhlc)
            # (Pdb) pandas.tseries.converter._dt_to_float_ordinal(mFeedOhlc.index)[0]
            # 735235.33333333337
            nDates = matplotlib.dates.date2num(mFeedOhlc.index.to_pydatetime())
            nVolume = 1000*np.random.normal(size=len(mFeedOhlc))

            self.vWarn("This may take minutes to display depending on your computer's speed")
            vGraphData(sSymbol, nDates,
                       mFeedOhlc.C.values, mFeedOhlc.H.values, mFeedOhlc.L.values, mFeedOhlc.O.values,
                       nVolume,
                       **_dPlotParams)

        self.vError("Unrecognized feed command: " + str(oArgs) +'\n' +__doc__)
        return

    if lArgs[0] == 'recipe':
        __doc__ = sBACrecipe__doc__
        from .Omlettes import lKnownRecipes
        # self.vDebug("lKnownRecipes: " + repr(lKnownRecipes))

        _lCmds = ['set', 'list', 'get', 'make', 'ingredients']

        sCmd = str(lArgs[1])
        if sCmd == 'list':
            self.poutput("Known Recipes: %r" % (self.G(lKnownRecipes,)))
            return

        if sCmd == 'get' or (sCmd == 'set' and len(lArgs) == 2):
            self.poutput("Current Recipe: %s" % (self.sRecipe,))
            return

        assert len(lArgs) > 1, "ERROR: not enough args: " +lArgs[0] +str(_lCmds)
        assert sCmd in _lCmds, "ERROR: %s %s not in: %r " % (
            lArgs[0], sCmd, _lCmds)

        if sCmd == 'set':
            assert len(lArgs) > 2, \
                   "ERROR: %s %s requires one of: %s" % (
                lArgs[0], sCmd, '|'.join(lKnownRecipes))
            sNewRecipe = str(lArgs[2])
            assert sNewRecipe in lKnownRecipes, \
                   "ERROR: %s %s %s not in: %s" % (
                lArgs[0], sCmd, sNewRecipe, '|'.join(lKnownRecipes))
            if self.sRecipe != sNewRecipe:
                self.sRecipe = sNewRecipe
                oRecipe = oEnsureRecipe(self, oOpts, sNewRecipe=sNewRecipe)
            #? do we update the config file? - I think not
            #? self.oConfig['backtest']['sRecipe'] = sNewRecipe
            return

        # The following all require that a feed has been loaded
        assert sFEED_CACHE_KEY
        assert sFEED_CACHE_KEY in dFEED_CACHE
        _dCurrentFeedFrame = dFEED_CACHE[sFEED_CACHE_KEY]
        assert _dCurrentFeedFrame
        if sCmd == 'make' or sCmd == 'ingredients':
            assert _dCurrentFeedFrame
            oRecipe = oEnsureRecipe(self, oOpts)
            # ugly
            dFeedParams = _dCurrentFeedFrame
            mFeedOhlc = _dCurrentFeedFrame['mFeedOhlc']
            dFeeds = dict(mFeedOhlc=mFeedOhlc, dFeedParams=dFeedParams)
            dRecipeParams = oRecipe.dRecipeParams()
            dIngredientsParams = dict(dRecipeParams=dRecipeParams)

            oRecipe.dMakeIngredients(dFeeds, dIngredientsParams)
            assert oRecipe.dIngredients
            return
        
        self.vError("Unrecognized recipe command: " + str(oArgs) +'\n' +__doc__)
        return

    if lArgs[0] == 'chef':
        __doc__ = sBACchef__doc__
        from .Omlettes import lKnownChefs
        # self.vDebug("lKnownChefs: " + repr(lKnownChefs))

        _lCmds = ['get', 'set', 'list', 'cook']
        assert len(lArgs) > 1, "ERROR: not enough args: " +lArgs[0] +str(_lCmds)
        sCmd = lArgs[1]
        
        if sCmd == 'list':
            self.poutput("Known Chefs: %r" % (lKnownChefs,))
            return

        if sCmd == 'get' or (sCmd == 'set' and len(lArgs) == 2):
            self.poutput("Current Chef: %s" % (self.sChef,))
            return

        assert sCmd in _lCmds, "ERROR: not in: " +lArgs[0] +str(_lCmds)

        if sCmd == 'set':
            assert len(lArgs) > 2, \
                   "ERROR: %s %s %s one of: %s" % (
                lArgs[0], sCmd, '|'.join(lKnownChefs))
            sNewChef = str(lArgs[2])
            assert sNewChef in lKnownChefs, \
                   "ERROR: %s %s %s not in: %s" % (
                lArgs[0], sCmd, sNewChef, '|'.join(lKnownChefs))
            if self.sChef != sNewChef:
                self.sChef = sNewChef
                oChef = oEnsureChef(self, oOpts, sNewChef=sNewChef)
            #? do we update the config file? - I think not
            #? self.oConfig['backtest']['sChef'] = sNewChef
            return

        # The following all require that a feed has been loaded
        assert sFEED_CACHE_KEY
        assert sFEED_CACHE_KEY in dFEED_CACHE
        _dCurrentFeedFrame = dFEED_CACHE[sFEED_CACHE_KEY]
        assert _dCurrentFeedFrame
        
        # There's always a default provided of these
        oOm = oEnsureOmlette(self, oOpts)
        oRecipe = oEnsureRecipe(self, oOpts)
        oChefModule = oEnsureChef(self, oOpts)

        if sCmd == 'cook':
            from .OTBackTest import oPyBacktestCook
            assert oRecipe.dIngredients
            # ugly
            dFeeds = _dCurrentFeedFrame
            
            oBt = oPyBacktestCook(dFeeds, oRecipe, oChefModule, oOm)
            assert oBt is not None
            if type(oBt) == str:
                raise RuntimeError(oBt)
            oOm.oBt = oBt
            # self.vDebug("Cooked " + oBt.sSummary())
            return
        
        self.vError("Unrecognized chef command: " + str(oArgs) +'\n' +__doc__)
        return

    if lArgs[0] == 'servings':
        __doc__ = sBACservings__doc__
        oOm = oEnsureOmlette(self, oOpts)
        oRecipe = oEnsureRecipe(self, oOpts)
        oChefModule = oEnsureChef(self, oOpts)

        if not hasattr(oOm, 'oBt') or not oOm.oBt:
            self.vError("You must use \"chef cook\" before you can have servings")
            return
        oBt = oOm.oBt

        # ['signals', 'trades', 'positions', 'equity', 'summary', 'trade_price']
        _lCmds = oChefModule.lProducedServings
        
        assert len(lArgs) > 1, "ERROR: argument required" +lArgs[0] +str(_lCmds)
        sCmd = lArgs[1]
        
        if sCmd == 'list':
            self.poutput("Produced Servings: %r" % (_lCmds,))
            return

        # self.vDebug("lProducedServings: " + repr(_lCmds))
        assert sCmd in _lCmds, "ERROR: %s %s not in %r" % (
            lArgs[0], sCmd, _lCmds)

        oFd = sys.stdout
        ## oFun = getattr(self.oBt, sCmd)
        ## self.poutput(oFun())
        if sCmd == 'signals':
            # this was the same as: oBt._mSignals = bt.mSignals() or oBt.signals
            oBt._mSignals = oRecipe.mSignals(oBt)
            oFd.write('INFO:  bt.signals found: %d\n' % len(oBt.signals))
            oOm.vAppendHdf('recipe/servings/mSignals', oBt.signals)
            return
            
        if sCmd == 'trades':
            # this was the same as: oBt._mTrades =  oBt.mTrades() or oBt.trades
            oBt._mTrades = oRecipe.mTrades(oBt)
            oFd.write('INFO:  bt.trades found: %d\n' % len(oBt.trades))
            oOm.vAppendHdf('recipe/servings/mTrades', oBt.trades)
            return
            
        if sCmd == 'positions':
            # this was the same as: oBt._rPositions = oBt.rPositions() or oBt.positions
            oBt._rPositions = oRecipe.rPositions(oBt, init_pos=0)
            oFd.write('INFO:  bt.positions found: %d\n' % len(oBt.positions))
            oOm.vAppendHdf('recipe/servings/rPositions', oBt.positions)
            return
            
        if sCmd == 'equity':
            # this was the same as: oBt._rEquity = oBt.rEquity() or oBt.equity
            oBt._rEquity = oRecipe.rEquity(oBt)
            oFd.write('INFO:  bt.equity found: %d\n' % len(oBt.equity))
            oOm.vAppendHdf('recipe/servings/rEquity', oBt.equity)
            return
            
        if sCmd == 'trade_price':
            # oFd.write('INFO:  bt.rTradePrice() found: %d\n' % len(oBt.rTradePrice()))
            oFd.write('INFO:  bt.trade_price found: %d\n' % len(oBt.trade_price))
            oOm.vAppendHdf('recipe/servings/rTradePrice', oBt.trade_price)
            return
            
        if sCmd == 'summary':
            oOm.vSetTitleHdf('recipe/servings', oOm.oChefModule.sChef)
            #? Leave this as derived or store it? reviews?
            oOm.vSetMetadataHdf('recipe/servings', oBt.dSummary())
            oFd.write(oBt.sSummary())
            return
            
        self.vError("Unrecognized servings command: " + str(oArgs) +'\n' +__doc__)
        return

    if lArgs[0] == 'plot':
        __doc__ = sBACplot__doc__
        _lCmds = ['show', 'set', 'trades', 'equity']
        
        assert len(lArgs) > 1, "ERROR: " +lArgs[0] +str(_lCmds)
        sCmd = lArgs[1]
        assert sCmd in _lCmds, "ERROR: " +lArgs[0] +str(_lCmds)

        import matplotlib.pylab as pylab
        if sCmd == 'show':
            pylab.show()
            return
        if sCmd == 'set':
            #?
            pylab.show()
            return

        assert len(lArgs) > 2, "ERROR: " +lArgs[0] +str(_lCmds)
        sCmd = lArgs[2]
        assert sCmd in _lCmds, "ERROR: " +lArgs[0] +str(_lCmds)
        oFun = getattr(self.oBt, 'plot_' + sCmd)
        oFun()
        pylab.show()
        return

    self.vError("Unrecognized backtest command: " + str(oArgs) +"\n" + sBAC__doc__)
