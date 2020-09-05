# -*- coding: UTF-8 -*-
import os
import unittest

from sppas.src.config import paths
from sppas.src.exceptions import sppasTypeError, sppasValueError
from sppas.src.utils.makeunicode import u
from sppas.src.resources import sppasDictRepl
from sppas.src.annotations.TextNorm.num2letter import sppasNum
from sppas.src.annotations.TextNorm.num2text.construct import sppasNumConstructor

# ---------------------------------------------------------------------------


ref_spa = [
    u("cero"),
    u("uno"),
    u("dos"),
    u("tres"),
    u("cuatro"),
    u("cinco"),
    u("seis"),
    u("siete"),
    u("ocho"),
    u("nueve"),
    u("diez"),
    u("once"),
    u("doce"),
    u("trece"),
    u("catorce"),
    u("quince"),
    u("dieciséis"),
    u("diecisiete"),
    u("dieciocho"),
    u("diecinueve"),
    u("veinte"),
    u("veintiuno"),
    u("veintidós"),
    u("veintitrés"),
    u("veinticuatro"),
    u("veinticinco"),
    u("veintiséis"),
    u("veintisiete"),
    u("veintiocho"),
    u("veintinueve"),
    u("treinta"),
    u("treinta-y-uno"),
    u("treinta-y-dos"),
    u("treinta-y-tres"),
    u("treinta-y-cuatro"),
    u("treinta-y-cinco"),
    u("treinta-y-seis"),
    u("treinta-y-siete"),
    u("treinta-y-ocho"),
    u("treinta-y-nueve"),
    u("cuarenta")
]

# ---------------------------------------------------------------------------


class TestNum2Text(unittest.TestCase):

    def setUp(self):

        class Hello(object):
            def __init__(self):
                pass
        self.hello = Hello()

        # Dictionaries actually created in normalize.py
        self.dict_fra = sppasDictRepl(os.path.join(paths.resources, 'num', 'fra_num.repl'), nodump=True)
        self.dict_eng = sppasDictRepl(os.path.join(paths.resources, 'num', 'eng_num.repl'), nodump=True)
        self.dict_jpn = sppasDictRepl(os.path.join(paths.resources, 'num', 'jpn_num.repl'), nodump=True)
        self.dict_spa = sppasDictRepl(os.path.join(paths.resources, 'num', 'spa_num.repl'), nodump=True)
        self.dict_por = sppasDictRepl(os.path.join(paths.resources, 'num', 'por_num.repl'), nodump=True)
        self.dict_ita = sppasDictRepl(os.path.join(paths.resources, 'num', 'ita_num.repl'), nodump=True)
        self.dict_khm = sppasDictRepl(os.path.join(paths.resources, 'num', 'khm_num.repl'), nodump=True)
        self.dict_pol = sppasDictRepl(os.path.join(paths.resources, 'num', 'pol_num.repl'), nodump=True)
        self.dict_vie = sppasDictRepl(os.path.join(paths.resources, 'num', 'vie_num.repl'), nodump=True)
        self.dict_cmn = sppasDictRepl(os.path.join(paths.resources, 'num', 'cmn_num.repl'), nodump=True)

        # new converter
        self.num_fra = sppasNumConstructor.construct('fra', self.dict_fra)
        self.num_eng = sppasNumConstructor.construct('eng', self.dict_eng)
        self.num_jpn = sppasNumConstructor.construct('jpn', self.dict_jpn)
        self.num_spa = sppasNumConstructor.construct('spa', self.dict_spa)
        self.num_por = sppasNumConstructor.construct('por', self.dict_por)
        self.num_ita = sppasNumConstructor.construct('ita', self.dict_ita)
        self.num_khm = sppasNumConstructor.construct('khm', self.dict_khm)
        self.num_pol = sppasNumConstructor.construct('pol', self.dict_pol)
        self.num_vie = sppasNumConstructor.construct('vie', self.dict_vie)
        self.num_cmn = sppasNumConstructor.construct('cmn', self.dict_cmn)

        # old converter
        self.old_num_fra = sppasNum('fra')
        self.old_num_eng = sppasNum('eng')
        self.old_num_jpn = sppasNum('jpn')
        self.old_num_spa = sppasNum('spa')
        self.old_num_por = sppasNum('por')
        self.old_num_ita = sppasNum('ita')
        self.old_num_khm = sppasNum('khm')
        self.old_num_pol = sppasNum('pol')
        self.old_num_vie = sppasNum('vie')
        self.old_num_cmn = sppasNum('cmn')

    # -----------------------------------------------------------------------

    def test_exc(self):
        # Known language
        with self.assertRaises(ValueError):
            self.num_fra.convert('3.0')

        with self.assertRaises(sppasValueError) as error:
            sppasNumConstructor.construct(18, self.dict_eng)
            self.assertTrue(isinstance(error.exception, sppasValueError))

        with self.assertRaises(sppasTypeError) as error:
            sppasNumConstructor.construct('fra', 18)
            self.assertTrue(isinstance(error.exception, sppasValueError))

        with self.assertRaises(sppasValueError) as error:
            sppasNumConstructor.construct('ger')
            self.assertTrue(isinstance(error.exception, sppasValueError))

    # -----------------------------------------------------------------------

    def test_convert(self):
        res_million_fra = self.num_fra.convert(1000000)
        res_eng = self.num_eng.convert(123456789)
        res_zero_english = self.num_eng.convert('00000123')
        res_jpn = self.num_jpn.convert(123456789)
        res_jpn_twenty = self.num_jpn.convert(22)

        self.assertEqual('un_million', res_million_fra)
        self.assertEqual('hundred_twenty_three_million_four_hundred_fifty_six_thousand_seven_hundred_eighty_nine', res_eng)
        self.assertEqual('zero_zero_zero_zero_zero_hundred_twenty_three', res_zero_english)
        self.assertEqual(u('一億二千三百四十五万六千七百八十九'), res_jpn)
        self.assertEqual(u('二十二'), res_jpn_twenty)

    # -----------------------------------------------------------------------

    def test_fra(self):
        """... number to letter in French """
        self.assertEqual(u("trois"),
                         self.num_fra.convert("3"))

        self.assertEqual(u("zéro_trois"),
                         self.num_fra.convert("03"))

        self.assertEqual(u("douze"),
                         self.num_fra.convert("12"))

        self.assertEqual(u("cent_vingt_trois"),
                         self.num_fra.convert("123"))

        self.assertEqual(u("cent_vingt-et-un"),
                         self.num_fra.convert("121"))

        self.assertEqual('cent_vingt_trois_million_quatre_cent_cinquante_six_mille_sept_cent_quatre-vingt_neuf',
                         self.num_fra.convert(123456789))

    # -----------------------------------------------------------------------

    def test_spa(self):
        """... number to letter in Spanish  """
        ret = [self.num_spa.convert(i) for i in range(41)]
        self.assertEqual(ref_spa, ret)

        self.assertEqual(u("mil-doscientos-cuarenta-y-uno"),
                         self.num_spa.convert(1241))

        self.assertEqual(u("dos-millones-trescientos-cuarenta-y-seis-mil-veintidós"),
                         self.num_spa.convert(2346022))

        self.assertEqual(u("trescientos-ochenta-y-dos-mil-ciento-veintiuno"),
                         self.num_spa.convert(382121))

        self.assertEqual(u("setecientos-treinta-y-nueve-mil-cuatrocientos-noventa-y-nueve"),
                         self.num_spa.convert(739499))

    # -----------------------------------------------------------------------

    def test_por(self):
        """... number to letter in portuguese"""
        por_old_conv_for_hundreds = [self.old_num_por.convert(str(i)) for i in range(500)]
        por_new_conv_for_hundreds = [self.num_por.convert(i) for i in range(500)]

        self.assertEqual(por_old_conv_for_hundreds, por_new_conv_for_hundreds)

        por_old_conv_for_thousand = [self.old_num_por.convert(str(i)) for i in range(1000, 2000)]
        por_new_conv_for_thousand = [self.num_por.convert(i) for i in range(1000, 2000)]

        self.assertEqual(por_old_conv_for_thousand, por_new_conv_for_thousand)

        self.assertEqual(u('um-milhão-duzentos-e-seis'), self.num_por.convert(1000206))

        self.assertEqual(u('setecentos-milhões-quatrocentos-e-seis'), self.num_por.convert(700000406))

    # -----------------------------------------------------------------------

    def test_ita(self):
        """... number to letter in italian"""
        self.assertEqual(u('nove'), self.num_ita.convert(9))
        self.assertEqual(u('ventidue'), self.num_ita.convert(22))
        self.assertEqual(u('quattrocentosessantadue'), self.num_ita.convert(462))
        self.assertEqual(u('settemiladuecentoquarantacinque'), self.num_ita.convert(7245))
        self.assertEqual(u('un_milione_duemilaottantadue'), self.num_ita.convert(1002082))
        self.assertEqual(u('un_miliardo_duemilaottantadue'), self.num_ita.convert(1000002082))

    # -----------------------------------------------------------------------

    def test_khm(self):
        """... number to letter in Khmer"""
        self.assertEqual(u('ប្រាំបួន'), self.num_khm.convert(9))
        self.assertEqual(u('ម្ភៃពីរ'), self.num_khm.convert(22))
        self.assertEqual(u('បួនរយហុកសិបពីរ'), self.num_khm.convert(462))
        self.assertEqual(u('ប្រាំពីរពាន់ពីររយសែសិបប្រាំ'), self.num_khm.convert(7245))
        self.assertEqual(u('មួយយលានពីរពាន់ប៉ែតសិបពីរ'), self.num_khm.convert(1002082))
        self.assertEqual(u('មួយយពាន់លានពីរពាន់ប៉ែតសិបពីរ'), self.num_khm.convert(1000002082))

    # -----------------------------------------------------------------------

    def test_pol(self):
        """... number to letter in Polish"""
        pol_old_conv_for_tenth = [self.old_num_pol.convert(str(i)) for i in range(2, 20)]
        pol_new_conv_for_tenth = [self.num_pol.convert(i) for i in range(2, 20)]

        self.assertEqual(pol_old_conv_for_tenth, pol_new_conv_for_tenth)

        self.assertEqual(u('dwadzieścia_dwa'), self.num_pol.convert(22))
        self.assertEqual(u('czterysta_sześćdziesiąt_dwa'), self.num_pol.convert(462))
        self.assertEqual(u('siedem_tysięcy_dwieście_czterdzieści_pięć'), self.num_pol.convert(7245))
        self.assertEqual(u('milion_dwa_tysiące_osiemdziesiąt_dwa'), self.num_pol.convert(1002082))
        self.assertEqual(u('miliard_dwa_tysiące_osiemdziesiąt_dwa'), self.num_pol.convert(1000002082))

    # -----------------------------------------------------------------------

    def test_vie(self):
        """... number to letter in Vietnamese"""
        self.assertEqual(u('hai_mươi_hai'), self.num_vie.convert(22))
        self.assertEqual(u('bốn_trăm_sáu_mươi_hai'), self.num_vie.convert(462))
        self.assertEqual(u('bảy_nghìn_hai_trăm_bốn_mươi_lăm'), self.num_vie.convert(7245))
        self.assertEqual(u('một_triệu_hai_nghìn_tám_mươi_hai'), self.num_vie.convert(1002082))
        self.assertEqual(u('một_tỷ_hai_nghìn_tám_mươi_hai'), self.num_vie.convert(1000002082))

    # -----------------------------------------------------------------------

    def test_cmn(self):
        """... number to letter in mandarin chinese"""
        cmn_old_conv_for_hundreds = [self.old_num_cmn.convert(str(i)) for i in range(20, 110)]
        cmn_new_conv_for_hundreds = [self.num_cmn.convert(i) for i in range(20, 110)]

        self.assertEqual(cmn_old_conv_for_hundreds, cmn_new_conv_for_hundreds)

        self.assertEqual(u('二十二'), self.num_cmn.convert(22))
        self.assertEqual(u('四百零六十二'), self.num_cmn.convert(462))
        self.assertEqual(u('七千二百零四十五'), self.num_cmn.convert(7245))
        self.assertEqual(u('一百万二千八十二'), self.num_cmn.convert(1002082))
        self.assertEqual(u('十亿二千八十二'), self.num_cmn.convert(1000002082))
