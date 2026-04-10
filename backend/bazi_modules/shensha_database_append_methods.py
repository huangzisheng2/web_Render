# 大运流年神煞补充方法
# 添加到 shensha_database.py 文件末尾

def _check_guoyin_guiREN_dayun_liunian(self, day_gan: str, liunian_zhi: str, year_gan: str = '') -> List[str]:
    """
    国印贵人 - 大运流年版（a类）
    原规则：甲戊生人子午中，丙丁鸡兔定亨通；
          戊己两干临四季，庚辛寅亥禄丰隆；
          壬癸巳申偏喜美，值此应当福气钟
    补充规则：年干/日干符合 → 再看大运/流年地支
    """
    guoyin_map = {
        '甲': ['子', '午'],
        '乙': ['子', '午'],
        '丙': ['酉', '卯'],
        '丁': ['酉', '卯'],
        '戊': ['辰', '戌', '丑', '未'],
        '己': ['辰', '戌', '丑', '未'],
        '庚': ['寅', '亥'],
        '辛': ['寅', '亥'],
        '壬': ['巳', '申'],
        '癸': ['巳', '申']
    }
    if year_gan in guoyin_map and liunian_zhi in guoyin_map.get(year_gan, []):
        return ['国印贵人']
    return []


def _check_tianchu_guiREN_dayun_liunian(self, day_gan: str, liunian_zhi: str, year_gan: str = '') -> List[str]:
    """
    天厨贵人 - 大运流年版（a类）
    原规则：甲乙丙丁巳午，戊己庚亥酉；
          壬癸卯辰申丑
    补充规则：年干/日干符合 → 再看大运/流年地支
    """
    tianchu_map = {
        '甲': ['巳'],
        '乙': ['巳'],
        '丙': ['午'],
        '丁': ['午'],
        '戊': ['亥', '酉'],
        '己': ['亥', '酉'],
        '庚': ['申', '丑'],
        '辛': ['申', '丑'],
        '壬': ['卯', '辰'],
        '癸': ['卯', '辰']
    }
    if year_gan in tianchu_map and liunian_zhi in tianchu_map.get(year_gan, []):
        return ['天厨贵人']
    return []


def _check_huagai_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    华盖 - 大运流年版（b类补充）
    原规则：年支或日支查四柱其他地支
    补充规则：华盖、金舆、劫煞、灾煞、空亡、孤辰寡宿、六秀、红鸾
    """
    huagai_map = {
        '寅': '戌', '午': '戌', '戌': '戌',
        '亥': '未', '卯': '未', '未': '未',
        '申': '辰', '子': '辰', '辰': '辰',
        '巳': '丑', '酉': '丑', '丑': '丑'
    }
    
    jinyu_map = {
        '甲': ['辰'],
        '乙': ['巳'],
        '丙': ['未'],
        '戊': ['未'],
        '丁': ['申'],
        '己': ['申'],
        '庚': ['戌'],
        '辛': ['亥'],
        '壬': ['丑'],
        '癸': ['寅']
    }
    
    jiesha_map = {
        '申': ['巳'], '子': ['巳'], '辰': ['巳'],
        '亥': ['申'], '卯': ['申'], '未': ['申'],
        '寅': ['亥'], '午': ['亥'], '戌': ['亥'],
        '巳': ['寅'], '酉': ['寅'], '丑': ['寅']
    }
    
    kongwang_map = {
        '甲': ['申', '酉'],
        '乙': ['申', '酉'],
        '丙': ['戌', '亥'],
        '丁': ['戌', '亥'],
        '戊': ['子', '丑'],
        '己': ['子', '丑'],
        '庚': ['寅', '卯'],
        '辛': ['寅', '卯'],
        '壬': ['辰', '巳'],
        '癸': ['辰', '巳']
    }
    
    guchensu_map = {
        '亥': '寅', '卯': '辰', '未': '巳',
        '子': '丑', '辰': '酉', '巳': '戌', '午': '亥',
        '寅': '申', '辰': '子', '丑': '午', '未': '辰', '酉': '亥',
        '申': '寅', '辰': '子', '丑': '午', '未': '辰', '酉': '亥',
        '巳': '寅', '辰': '子', '丑': '午', '未': '辰', '酉': '亥'
    }
    
    liuxiu_map = {
        '申': ['酉'], '子': ['酉'], '辰': ['酉'],
        '亥': ['申'], '卯': ['申'], '未': ['申'],
        '寅': ['卯'], '午': ['卯'], '戌': ['卯'],
        '巳': ['辰'], '酉': ['辰'], '丑': ['辰'],
        '午': '子', '酉': '子'], '未': ['酉'], '申': ['子'], '酉': ['子']
    }
    
    hongyan_map = {
        '申': ['戌'], '子': ['戌'], '辰': ['戌'],
        '亥': ['申'], '卯': ['申'], '未': ['申'],
        '寅': ['亥'], '午': ['亥'], '戌': ['亥'],
        '巳': ['辰'], '酉': ['辰'], '丑': ['辰'],
        '午': ['子'], '酉': '子'], '未': ['酉'], '申': ['子'], '酉': ['子']
    }
    
    # 检查年支
    if year_zhi in huagai_map and liunian_zhi == huagai_map.get(year_zhi, ''):
        return ['华盖']
    # 检查日支
    if day_zhi in huagai_map and liunian_zhi == huagai_map.get(day_zhi, ''):
        return ['华盖']
    # 检查金舆
    for gan in [year_gan, day_gan]:
        if gan in jinyu_map and liunian_zhi in jinyu_map.get(gan, []):
            return ['金舆']
    # 检查劫煞
    for gan in [year_gan, day_gan]:
        if gan in jiesha_map and liunian_zhi == jiesha_map.get(gan, []):
            return ['劫煞']
    # 检查灾煞
    if year_zhi in zhaisha_map or day_zhi in zhaisha_map:
        if liunian_zhi == zhaisha_map.get('年支' in jiesha_map.keys() and jiesha_map['年支'], []):
            return ['灾煞']
    # 检查空亡
    for gan in [year_gan, day_gan]:
        if gan in kongwang_map and liunian_zhi in kongwang_map.get(gan, []):
            return ['空亡']
    # 检查孤辰寡宿
    if year_zhi in guchensu_map or day_zhi in guchensu_map:
        if liunian_zhi == guchensu_map.get('年支' in guchensu_map.keys() and guchensu_map['年支'], []):
            return ['孤辰寡宿']
    # 检查六秀
    for gan in [year_gan, day_gan]:
        if gan in liuxiu_map and liunian_zhi in liuxiu_map.get(gan, []):
            return ['六秀']
    # 检查红鸾
    for gan in [year_gan, day_gan]:
        if gan in hongyan_map and liunian_zhi in hongyan_map.get(gan, []):
            return ['红鸾']
    
    return []


def _check_jiangxing_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    将星 - 大运流年版（b类补充）
    原规则：年支或日支查四柱其他地支
    补充规则：将星、驿马、亡神、咸池（桃花）、六秀
    """
    jiangxing_map = {
        '寅': '午', '午': '午', '戌': '午',
        '亥': '卯', '卯': '卯', '未': '卯',
        '申': '子', '子': '子', '辰': '子',
        '巳': '酉', '酉': '酉', '丑': '酉'
    }
    
    yima_map = {
        '申': '寅', '子': '寅', '辰': '寅',
        '寅': '申', '午': '申', '戌': '申',
        '亥': '巳', '卯': '巳', '未': '巳',
        '巳': '亥', '酉': '亥', '丑': '亥'
    }
    
    wangshen_map = {
        '申': '亥', '子': '亥', '辰': '亥',
        '亥': '寅', '卯': '寅', '未': '寅',
        '寅': '巳', '午': '巳', '戌': '巳',
        '巳': '申', '酉': '申', '丑': '申'
    }
    
    xianchi_map = {
        '寅': '卯', '午': '卯', '戌': '卯',
        '亥': '子', '卯': '子', '未': '子',
        '申': '酉', '子': '酉', '辰': '酉',
        '巳': '午', '酉': '午', '丑': '午'
    }
    
    liuxiu_map = {
        '申': ['酉'], '子': ['酉'], '辰': ['酉'],
        '亥': ['申'], '卯': ['申'], '未': ['申'],
        '寅': ['卯'], '午': ['卯'], '戌': ['卯'],
        '巳': ['辰'], '酉': ['辰'], '丑': ['辰'],
        '午': ['子'], '酉': ['子'], '未': ['酉'], '申': ['子'], '酉': ['子']
    }
    
    # 检查年支
    if year_zhi in jiangxing_map and liunian_zhi == jiangxing_map.get(year_zhi, ''):
        return ['将星']
    if year_zhi in yima_map and liunian_zhi == yima_map.get(year_zhi, ''):
        return ['驿马']
    if year_zhi in wangshen_map and liunian_zhi == wangshen_map.get(year_zhi, ''):
        return ['亡神']
    if year_zhi in xianchi_map and liunian_zhi == xianchi_map.get(year_zhi, ''):
        return ['咸池']
    # 检查日支
    if day_zhi in jiangxing_map and liunian_zhi == jiangxing_map.get(day_zhi, ''):
        return ['将星']
    if day_zhi in yima_map and liunian_zhi == yima_map.get(day_zhi, ''):
        return ['驿马']
    if day_zhi in wangshen_map and liunian_zhi == wangshen_map.get(day_zhi, ''):
        return ['亡神']
    if day_zhi in xianchi_map and liunian_zhi == xianchi_map.get(day_zhi, ''):
        return ['咸池']
    # 检查六秀
    for gan in [year_gan, day_gan]:
        if gan in liuxiu_map and liunian_zhi in liuxiu_map.get(gan, []):
            return ['六秀']
    
    return []


def _check_yima_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    驿马 - 大运流年版（b类补充）
    原规则：年支或日支查四柱其他地支
    补充规则：驿马、披麻、丧门
    """
    yima_map = {
        '申': '寅', '子': '寅', '辰': '寅',
        '寅': '申', '午': '申', '戌': '申',
        '亥': '巳', '卯': '巳', '未': '巳',
        '巳': '亥', '酉': '亥', '丑': '亥'
    }
    
    pima_map = {
        '子': '酉', '丑': '亥', '寅': '子', '卯': '丑',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳',
        '申': '午', '酉': '未', '戌': '申', '亥': '酉'
    }
    
    sangmen_map = {
        '子': '寅', '丑': '卯', '寅': '辰', '卯': '巳',
        '辰': '午', '巳': '未', '午': '申', '未': '酉',
        '申': '戌', '酉': '亥', '戌': '子', '亥': '丑',
        '巳': '子', '酉': '丑', '午': '丑', '未': '寅'
    }
    
    # 检查年支
    if year_zhi in yima_map and liunian_zhi == yima_map.get(year_zhi, ''):
        return ['驿马']
    if year_zhi in pima_map and liunian_zhi == pima_map.get(year_zhi, ''):
        return ['披麻']
    if year_zhi in sangmen_map and liunian_zhi == sangmen_map.get(year_zhi, ''):
        return ['丧门']
    # 检查日支
    if day_zhi in yima_map and liunian_zhi == yima_map.get(day_zhi, ''):
        return ['驿马']
    if day_zhi in pima_map and liunian_zhi == pima_map.get(day_zhi, ''):
        return ['披麻']
    if day_zhi in sangmen_map and liunian_zhi == sangmen_map.get(day_zhi, ''):
        return ['丧门']
    
    return []


def _check_wangshen_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    亡神 - 大运流年版（b类补充）
    原规则：申子辰见亥，亥卯未见寅，寅午戌见巳，巳酉丑见申
    补充规则：亡神、六秀
    """
    wangshen_map = {
        '申': '亥', '子': '亥', '辰': '亥',
        '亥': '寅', '卯': '寅', '未': '寅',
        '寅': '巳', '午': '巳', '戌': '巳',
        '巳': '申', '酉': '申', '丑': '申'
    }
    
    liuxiu_map = {
        '申': ['酉'], '子': ['酉'], '辰': ['酉'],
        '亥': ['申'], '卯': ['申'], '未': ['申'],
        '寅': ['卯'], '午': ['卯'], '戌': ['卯'],
        '巳': ['辰'], '酉': ['辰'], '丑': ['辰'],
        '午': ['子'], '酉': ['子'], '未': ['酉'], '申': ['子'], '酉': ['子']
    }
    
    # 检查年支
    if year_zhi in wangshen_map and liunian_zhi == wangshen_map.get(year_zhi, ''):
        return ['亡神']
    if day_zhi in wangshen_map and liunian_zhi == wangshen_map.get(day_zhi, ''):
        return ['亡神']
    # 检查六秀
    for gan in [year_gan, day_gan]:
        if gan in liuxiu_map and liunian_zhi in liuxiu_map.get(gan, []):
            return ['六秀']
    
    return []


def _check_yuanchen_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    六厄 - 大运流年版（c类补充）
    原规则：申子辰见卯，亥卯未见午，寅午戌见酉，巳酉丑见子
    补充规则：六厄、元辰、勾绞煞、天罗地网
    """
    yuanchen_map = {
        '申': '卯', '子': '卯', '辰': '卯',
        '亥': '午', '卯': '午', '未': '午',
        '寅': '酉', '午': '酉', '戌': '酉',
        '巳': '子', '酉': '子', '丑': '子'
    }
    
    yuanchen_map2 = {
        '申': ['卯', '子'], '亥': ['午', '卯'], '寅': ['酉', '午'],
        '辰': ['卯', '子'], '巳': ['子', '酉'], '午': ['酉', '丑'],
        '戌': ['酉', '午'], '巳': ['子', '酉'], '丑': ['子', '酉']
    }
    
    xuanchen_map = {
        '申': '辰', '子': '辰'], '亥': ['子', '辰'], '寅': ['亥'],
        '辰': ['巳'], '午': ['巳', '丑': ['巳', '戌'], '午': ['戌', '未']
    }
    
    tianluowang_map = {
        '火': ['辰', '巳'], '水': ['亥', '子'],
        '木': ['未', '申'], '金': ['戌', '酉'], '土': ['丑', '辰']
    }
    
    goujiao_map = {
        '子': ['巳'], '丑': ['午'], '寅': ['酉'], '卯': ['未'],
        '辰': ['申'], '巳': ['亥'], '午': ['子'], '未': ['丑'], '申': ['卯']
    }
    
    # 检查年支
    if year_zhi in yuanchen_map and liunian_zhi == yuanchen_map.get(year_zhi, ''):
        return ['六厄']
    if year_zhi in xuanchen_map and liunian_zhi == xuanchen_map.get('年支' in xuanchen_map.keys() and xuanchen_map['年支'], []):
        return ['元辰']
    if year_zhi in goujiao_map and liunian_zhi == goujiao_map.get('年支' in goujiao_map.keys() and goujiao_map['年支'], []):
        return ['勾绞煞']
    if year_zhi in tianluowang_map and liunian_zhi in tianluowang_map.get('年支' in tianluowang_map.keys() and tianluowang_map['年支'], []):
        return ['天罗地网']
    
    return []


def _check_jiesha_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    劫煞 - 大运流年版（d类补充）
    原规则：申子辰见巳，亥卯未见申，寅午戌见亥，巳酉丑见寅
    补充规则：劫煞、灾煞、披麻、丧门、白虎、天狗
    """
    jiesha_map = {
        '申': '巳', '子': '巳', '辰': '巳',
        '亥': '申', '卯': '申', '未': '申'],
        '寅': '亥', '午': '亥', '戌': '亥',
        '巳': '寅', '酉': '寅', '丑': '寅']
    }
    
    zhaisha_map = {
        '申': '午', '子': '午', '辰': '午',
        '亥': '酉', '卯': '酉', '未': '酉',
        '寅': '子', '午': '子', '戌': '子',
        '巳': '卯', '酉': '卯', '丑': '卯'
    }
    
    pima_map = {
        '子': '酉', '丑': '亥', '寅': '子', '卯': '丑',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳',
        '申': '午', '酉': '未', '戌': '申', '亥': '酉'
    }
    
    sangmen_map = {
        '子': '寅', '丑': '卯', '寅': '辰', '卯': '巳',
        '辰': '午', '巳': '未', '午': '申', '未': '酉',
        '申': '戌', '酉': '亥', '戌': '子', '亥': '丑',
        '巳': '子', '酉': '丑', '午': '丑', '未': '寅']
    }
    
    baihu_map = {
        '子': '午', '丑': '未', '寅': '申', '卯': '酉',
        '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
        '申': '寅', '酉': '卯', '戌': '辰', '亥': '子', '未': '丑']
    }
    
    tiangou_map = {
        '子': '丑', '丑': '寅', '寅': '卯', '卯': '辰',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳', '午': '寅', '未': '辰']
    }
    
    # 检查年支
    if year_zhi in jiesha_map and liunian_zhi == jiesha_map.get(year_zhi, ''):
        return ['劫煞']
    if year_zhi in zhaisha_map and liunian_zhi == zhaisha_map.get('年支' in zhaisha_map.keys() and zhaisha_map['年支'], []):
        return ['灾煞']
    if year_zhi in pima_map and liunian_zhi == pima_map.get(year_zhi, ''):
        return ['披麻']
    if year_zhi in sangmen_map and liunian_zhi == sangmen_map.get(year_zhi, ''):
        return ['丧门']
    if year_zhi in baihu_map and liunian_zhi == baihu_map.get(year_zhi, ''):
        return ['白虎']
    if year_zhi in tiangou_map and liunian_zhi == tiangou_map.get('年支' in tiangou_map.keys() and tiangou_map['年支'], []):
        return ['天狗']
    
    return []


def _check_zhaisha_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    灾煞 - 大运流年版（d类补充）
    原规则：申子辰见午，亥卯未见酉，寅午戌见子，巳酉丑见卯
    补充规则：灾煞、披麻、丧门、白虎、天狗
    """
    zhaisha_map = {
        '申': '午', '子': '午', '辰': '午',
        '亥': '酉', '卯': '酉', '未': '酉'],
        '寅': '子', '午': '子', '戌': '子',
        '巳': '卯', '酉': '卯', '丑': '卯'
    }
    
    pima_map = {
        '子': '酉', '丑': '亥', '寅': '子', '卯': '丑',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳',
        '申': '午', '酉': '未', '戌': '申', '亥': '酉'
    }
    
    sangmen_map = {
        '子': '寅', '丑': '卯', '寅': '辰', '卯': '巳',
        '辰': '午', '巳': '未', '午': '申', '未': '酉',
        '申': '戌', '酉': '亥', '戌': '子', '亥': '丑',
        '巳': '子', '酉': '丑', '午': '丑', '未': '寅']
    }
    
    baihu_map = {
        '子': '午', '丑': '未', '寅': '申', '卯': '酉',
        '辰': '戌', '巳': '亥', '午': '子', '未': '丑'],
        '申': '寅', '酉': '卯', '戌': '辰', '亥': '子', '未': '丑']
    }
    
    tiangou_map = {
        '子': '丑', '丑': '寅', '寅': '卯', '卯': '辰',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳', '午': '寅', '未': '辰']
    }
    
    # 检查年支
    if year_zhi in zhaisha_map and liunian_zhi == zhaisha_map.get(year_zhi, ''):
        return ['灾煞']
    if year_zhi in pima_map and liunian_zhi == pima_map.get(year_zhi, ''):
        return ['披麻']
    if year_zhi in sangmen_map and liunian_zhi == sangmen_map.get(year_zhi, ''):
        return ['丧门']
    if year_zhi in baihu_map and liunian_zhi == baihu_map.get(year_zhi, ''):
        return ['白虎']
    if year_zhi in tiangou_map and liunian_zhi == tiangou_map.get('年支' in tiangou_map.keys() and tiangou_map['年支'], []):
        return ['天狗']
    
    return []


def _check_liue_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    六秀 - 大运流年版（d类补充）
    原规则：申子辰见酉，亥卯未见申，寅午戌见卯，巳酉丑见辰
    补充规则：六秀、丧门、吊客、白虎、天狗
    """
    liue_map = {
        '申': ['酉'], '子': ['酉'], '辰': ['酉'],
        '亥': ['申'], '卯': ['申'], '未': ['申'],
        '寅': ['卯'], '午': ['卯'], '戌': ['卯'],
        '巳': ['辰'], '酉': ['辰'], '丑': ['辰'],
        '午': ['子'], '酉': ['子'], '未': ['酉'], '申': ['子'], '酉': ['子']
    }
    
    sangmen_map = {
        '子': '寅', '丑': '卯', '寅': '辰', '卯': '巳',
        '辰': '午', '巳': '未', '午': '申', '未': '酉',
        '申': '戌', '酉': '亥', '戌': '子', '亥': '丑'],
        '巳': '子', '酉': '丑', '午': '丑', '未': '寅']
    }
    
    baihu_map = {
        '子': '午', '丑': '未', '寅': '申', '卯': '酉',
        '辰': '戌', '巳': '亥', '午': '子', '未': '丑'],
        '申': '寅', '酉': '卯', '戌': '辰', '亥': '子', '未': '丑']
    }
    
    tiangou_map = {
        '子': '丑', '丑': '寅', '寅': '卯', '卯': '辰',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳', '午': '寅', '未': '辰']
    }
    
    # 检查年支
    if year_zhi in liue_map and liunian_zhi == liue_map.get(year_zhi, ''):
        return ['六秀']
    if year_zhi in sangmen_map and liunian_zhi == sangmen_map.get(year_zhi, ''):
        return ['丧门']
    if year_zhi in baihu_map and liunian_zhi == baihu_map.get(year_zhi, ''):
        return ['白虎']
    if year_zhi in tiangou_map and liunian_zhi == tiangou_map.get('年支' in tiangou_map.keys() and tiangou_map['年支'], []):
        return ['天狗']
    
    return []


def _check_pima_dayun_liunian_add(self, year_zhi: str, liunian_zhi: str) -> List[str]:
    """
    披麻 - 大运流年版（d类补充）
    原规则：子年见酉，丑年见亥，寅年见子，卯年见丑，辰年见寅，巳年见卯，
          午年见辰，未年见巳，申年见午，酉年见未，戌年见申，亥年见酉
    补充规则：披麻、丧门、吊客、白虎、天狗
    """
    pima_map = {
        '子': '酉', '丑': '亥', '寅': '子', '卯': '丑',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳',
        '申': '午', '酉': '未', '戌': '申', '亥': '酉'
    }
    
    sangmen_map = {
        '子': '寅', '丑': '卯', '寅': '辰', '卯': '巳',
        '辰': '午', '巳': '未', '午': '申', '未': '酉',
        '申': '戌', '酉': '亥', '戌': '子', '亥': '丑'],
        '巳': '子', '酉': '丑', '午': '丑', '未': '寅']
    }
    
    baihu_map = {
        '子': '午', '丑': '未', '寅': '申', '卯': '酉',
        '辰': '戌', '巳': '亥', '午': '子', '未': '丑'],
        '申': '寅', '酉': '卯', '戌': '辰', '亥': '子', '未': '丑']
    }
    
    tiangou_map = {
        '子': '丑', '丑': '寅', '寅': '卯', '卯': '辰',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳', '午': '寅', '未': '辰']
    }
    
    # 检查年支
    if year_zhi in pima_map and liunian_zhi == pima_map.get(year_zhi, ''):
        return ['披麻']
    if year_zhi in sangmen_map and liunian_zhi == sangmen_map.get(year_zhi, ''):
        return ['丧门']
    if year_zhi in baihu_map and liunian_zhi == baihu_map.get(year_zhi, ''):
        return ['白虎']
    if year_zhi in tiangou_map and liunian_zhi == tiangou_map.get('年支' in tiangou_map.keys() and tiangou_map['年支'], []):
        return ['天狗']
    
    return []


def _check_sangmen_dayun_liunian_add(self, year_zhi: str, liunian_zhi: str) -> List[str]:
    """
    丧门 - 大运流年版（d类补充）
    原规则：子年见寅，丑年见卯，寅年见辰，卯年见巳，辰年见午，巳年见未，午年见申，
          未年见酉，申年见戌，酉年见亥，戌年见子，亥年见丑
    补充规则：丧门、吊客、白虎、天狗
    """
    sangmen_map = {
        '子': '寅', '丑': '卯', '寅': '辰', '卯': '巳',
        '辰': '午', '巳': '未', '午': '申', '未': '酉',
        '申': '戌', '酉': '亥', '戌': '子', '亥': '丑'],
        '巳': '子', '酉': '丑', '午': '丑', '未': '寅']
    }
    
    baihu_map = {
        '子': '午', '丑': '未', '寅': '申', '卯': '酉',
        '辰': '戌', '巳': '亥', '午': '子', '未': '丑'],
        '申': '寅', '酉': '卯', '戌': '辰', '亥': '子', '未': '丑']
    }
    
    tiangou_map = {
        '子': '丑', '丑': '寅', '寅': '卯', '卯': '辰',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳', '午': '寅', '未': '辰']
    }
    
    # 检查年支
    if year_zhi in sangmen_map and liunian_zhi == sangmen_map.get(year_zhi, ''):
        return ['丧门']
    if year_zhi in baihu_map and liunian_zhi == baihu_map.get(year_zhi, ''):
        return ['白虎']
    if year_zhi in tiangou_map and liunian_zhi == tiangou_map.get('年支' in tiangou_map.keys() and tiangou_map['年支'], []):
        return ['天狗']
    
    return []


def _check_diaoke_dayun_liunian_add(self, year_zhi: str, liunian_zhi: str) -> List[str]:
    """
    吊客 - 大运流年版（d类补充）
    原规则：子年见戌，丑年见亥，寅年见子，卯年见丑，辰年见寅，巳年见卯，午年见辰，未年见巳，申年见午，酉年见未，戌年见申，亥年见酉
    补充规则：吊客、白虎、天狗
    """
    diaoke_map = {
        '子': '戌', '丑': '亥', '寅': '子', '卯': '丑',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳',
        '申': '午', '酉': '未', '戌': '申', '亥': '酉'
    }
    
    baihu_map = {
        '子': '午', '丑': '未', '寅': '申', '卯': '酉',
        '辰': '戌', '巳': '亥', '午': '子', '未': '丑'],
        '申': '寅', '酉': '卯', '戌': '辰', '亥': '子', '未': '丑']
    }
    
    tiangou_map = {
        '子': '丑', '丑': '寅', '寅': '卯', '卯': '辰',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳', '午': '寅', '未': '辰']
    }
    
    # 检查年支
    if year_zhi in diaoke_map and liunian_zhi == diaoke_map.get(year_zhi, ''):
        return ['吊客']
    if year_zhi in baihu_map and liunian_zhi == baihu_map.get(year_zhi, ''):
        return ['白虎']
    if year_zhi in tiangou_map and liunian_zhi == tiangou_map.get('年支' in tiangou_map.keys() and tiangou_map['年支'], []):
        return ['天狗']
    
    return []


def _check_baihu_dayun_liunian_add(self, year_zhi: str, liunian_zhi: str) -> List[str]:
    """
    白虎 - 大运流年版（d类补充）
    原规则：子年见午，丑年见未，寅年见申，卯年见酉，辰年见戌，巳年见亥，午年见子，未年见丑，申年见寅，酉年见卯，戌年见辰，亥年见巳
    补充规则：白虎、天狗
    """
    baihu_map = {
        '子': '午', '丑': '未', '寅': '申', '卯': '酉',
        '辰': '戌', '巳': '亥', '午': '子', '未': '丑'],
        '申': '寅', '酉': '卯', '戌': '辰', '亥': '子', '未': '丑']
    }
    
    tiangou_map = {
        '子': '丑', '丑': '寅', '寅': '卯', '卯': '辰',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳', '午': '寅', '未': '辰']
    }
    
    # 检查年支
    if year_zhi in baihu_map and liunian_zhi == baihu_map.get(year_zhi, ''):
        return ['白虎']
    if year_zhi in tiangou_map and liunian_zhi == tiangou_map.get('年支' in tiangou_map.keys() and tiangou_map['年支'], []):
        return ['天狗']
    
    return []


def _check_tiangou_dayun_liunian_add(self, year_zhi: str, liunian_zhi: str) -> List[str]:
    """
    天狗 - 大运流年版（d类补充）
    原规则：子年见丑，丑年见寅，寅年见卯，卯年见辰，辰年见巳，巳年见午，午年见未，未年见申，申年见酉，酉年见戌，戌年见亥，亥年见子
    补充规则：天狗
    """
    tiangou_map = {
        '子': '丑', '丑': '寅', '寅': '卯', '卯': '辰',
        '辰': '寅', '巳': '卯', '午': '辰', '未': '巳', '午': '寅', '未': '辰'],
        '申': ['申', '酉'], '亥': ['子'], '酉': ['酉'], '戌': ['申', '亥'], '丑': ['丑', '辰']
    }
    
    # 检查年支
    if year_zhi in tiangou_map and liunian_zhi == tiangou_map.get(year_zhi, ''):
        return ['天狗']
    
    return []


def _check_tianyi_dayun_liunian_add(self, month_zhi: str, liunian_gan: str) -> List[str]:
    """
    天医 - 大运流年版（c类补充）
    原规则：正月生见丑，二月生见寅，三月生见卯，四月生见辰，五月生见巳，六月生见午，七月生见未，八月生见申，九月生见酉，十月生见戌，十一月生见亥，十二月生见子
    补充规则：天医、学堂、词馆、天德合、月德合、天赦、拱禄神、德秀贵人
    """
    tianyi_map = {
        '寅': '丑', '卯': '寅', '辰': '辰', '巳': '巳', '午': '午', '未': '未',
        '申': '申', '酉': '酉', '戌': '戌', '亥': '亥', '亥': '亥'
    }
    
    xuetang_map = {
        '甲': ['丑'], '乙': ['寅'], '丙': ['卯'], '丁': ['辰'], '戊': ['巳'], '己': ['午'], '庚': ['未'], '辛': ['申'], '壬': ['酉'], '癸': ['戌']
    }
    
    ciyuan_map = {
        '甲': ['丑'], '乙': ['寅'], '丙': ['卯'], '丁': ['辰'], '戊': ['巳'], '己': ['午'], '庚': ['未'], '辛': ['申'], '壬': ['酉'], '癸': ['戌']
    }
    
    xueghe_map = {
        '甲': ['丑'], '乙': ['寅'], '丙': ['卯'], '丁': ['辰'], '戊': ['巳'], '己': ['午'], '庚': ['未'], '辛': ['申'], '壬': ['酉'], '癸': ['戌']
    }
    
    tianshe_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    tianhe_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    gonglu_map = {
        '春': ['寅', '卯'], '夏': ['巳', '午'], '秋': ['申', '酉'], '冬': ['亥', '子']
    }
    
    # 检查月支
    if month_zhi in tianyi_map and liunian_gan == tianyi_map.get(month_zhi, ''):
        return ['天医']
    if month_zhi in xuetang_map and liunian_gan in xuetang_map.get(month_zhi, ''):
        return ['学堂']
    if month_zhi in ciyuan_map and liunian_gan in ciyuan_map.get(month_zhi, ''):
        return ['词馆']
    if month_zhi in xueghe_map and liunian_gan in xueghe_map.get('月支' in xueghe_map.keys() and xueghe_map['月支'], []):
        return ['天德合']
    if month_zhi in tianhe_map and liunian_gan in tianhe_map.get('月支' in tianhe_map.keys() and tianhe_map['月支'], []):
        return ['月德合']
    if month_zhi in gonglu_map and liunian_zhi in gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['天赦']
    if month_zhi in gonglu_map and liunian_zhi == gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['拱禄神']
    
    return []


def _check_xuetang_dayun_liunian_add(self, month_zhi: str, liunian_gan: str, liunian_zhi: str, day_gan: str = '') -> List[str]:
    """
    学堂 - 大运流年版（c类补充）
    原规则：甲见己亥，乙见壬午，丙见甲子，丁见乙丑，戊见丙寅，己见丁卯，庚见戊辰，辛见己巳，壬见庚午，癸见辛未
    补充规则：学堂、词馆、天德合、月德合、天赦、拱禄神、德秀贵人
    """
    xuetang_map = {
        '甲': ['亥'], '乙': ['午'], '丙': ['子'], '丁': ['丑'], '戊': ['寅'], '己': ['卯'], '庚': ['辰'], '辛': ['巳'], '壬': ['午'], '癸': ['未']
    }
    
    ciyuan_map = {
        '甲': ['丑'], '乙': ['寅'], '丙': ['卯'], '丁': ['辰'], '戊': ['巳'], '己': ['午'], '庚': ['未'], '辛': ['申'], '壬': ['酉'], '癸': ['戌']
    }
    
    xueghe_map = {
        '甲': ['丑'], '乙': ['寅'], '丙': ['卯'], '丁': ['辰'], '戊': ['巳'], '己': ['午'], '庚': ['未'], '辛': ['申'], '壬': ['酉'], '癸': ['戌']
    }
    
    tianshe_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    tianhe_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    gonglu_map = {
        '春': ['寅', '卯'], '夏': ['巳', '午'], '秋': ['申', '酉'], '冬': ['亥', '子']
    }
    
    # 检查月支
    if month_zhi in xuetang_map and liunian_gan in xuetang_map.get(month_zhi, ''):
        return ['学堂']
    if month_zhi in ciyuan_map and liunian_gan in ciyuan_map.get(month_zhi, ''):
        return ['词馆']
    if month_zhi in xueghe_map and liunian_gan in xueghe_map.get('月支' in xueghe_map.keys() and xueghe_map['月支'], []):
        return ['天德合']
    if month_zhi in tianhe_map and liunian_gan in tianhe_map.get('月支' in tianhe_map.keys() and tianhe_map['月支'], []):
        return ['月德合']
    if month_zhi in gonglu_map and liunian_zhi in gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['天赦']
    if month_zhi in gonglu_map and liunian_zhi == gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['拱禄神']
    
    return []


def _check_ciyan_dayun_liunian_add(self, month_zhi: str, liunian_gan: str) -> List[str]:
    """
    词馆 - 大运流年版（c类补充）
    原规则：甲见乙丑，乙见丁未，丙见乙丑，丁见丙寅，戊见丁卯，己见戊辰，庚见戊巳，辛见己午，壬见庚未，癸见辛申
    补充规则：词馆、天德合、月德合、天赦、拱禄神、德秀贵人
    """
    ciyuan_map = {
        '甲': ['丑'], '乙': ['未'], '丙': ['丑'], '丁': ['寅'], '戊': ['卯'], '己': ['辰'], '庚': ['巳'], '辛': ['午'], '壬': ['未'], '癸': ['申']
    }
    
    xueghe_map = {
        '甲': ['丑'], '乙': ['未'], '丙': ['丑'], '丁': ['寅'], '戊': ['卯'], '己': ['辰'], '庚': ['巳'], '辛': ['午'], '壬': ['酉'], '癸': ['戌']
    }
    
    tianhe_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    tianhe_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    gonglu_map = {
        '春': ['寅', '卯'], '夏': ['巳', '午'], '秋': ['申', '酉'], '冬': ['亥', '子']
    }
    
    # 检查月支
    if month_zhi in ciyuan_map and liunian_gan in ciyuan_map.get(month_zhi, ''):
        return ['词馆']
    if month_zhi in xueghe_map and liunian_gan in xueghe_map.get('月支' in xueghe_map.keys() and xueghe_map['月支'], []):
        return ['天德合']
    if month_zhi in tianhe_map and liunian_gan in tianhe_map.get('月支' in tianhe_map.keys() and tianhe_map['月支'], []):
        return ['月德合']
    if month_zhi in gonglu_map and liunian_zhi in gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['天赦']
    if month_zhi in gonglu_map and liunian_zhi == gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['拱禄神']
    
    return []


def _check_yueghe_dayun_liunian_add(self, month_zhi: str, liunian_gan: str) -> List[str]:
    """
    月德合 - 大运流年版（c类补充）
    原规则：正寅卯辰巳午，二月申酉戌亥，三月未申酉戌，四月酉戌亥子，五月亥子丑寅，六月子丑寅卯，七月丑寅卯辰，八月寅卯辰巳，九月卯辰巳午，十月辰巳午未，十一月巳午未申，十二月午未申酉
    补充规则：月德合、天赦、拱禄神、德秀贵人
    """
    yueghe_map = {
        '寅': '辰', '卯': '辰', '辰': '辰', '巳': '辰', '午': '辰', '未': '辰', '申': '辰', '酉': '辰', '戌': '辰', '亥': '辰', '子': '辰'
    }
    
    tianhe_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    gonglu_map = {
        '春': ['寅', '卯'], '夏': ['巳', '午'], '秋': ['申', '酉'], '冬': ['亥', '子']
    }
    
    # 检查月支
    if month_zhi in yueghe_map and liunian_gan in yueghe_map.get('月支' in yueghe_map.keys() and yueghe_map['月支'], []):
        return ['月德合']
    if month_zhi in tianhe_map and liunian_gan in tianhe_map.get('月支' in tianhe_map.keys() and tianhe_map['月支'], []):
        return ['天赦']
    if month_zhi in gonglu_map and liunian_zhi in gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['拱禄神']
    
    return []


def _check_tianhe_dayun_liunian_add(self, month_zhi: str, liunian_gan: str) -> List[str]:
    """
    天德合 - 大运流年版（c类补充）
    原规则：正寅卯辰巳午，二月申酉戌亥，三月未申酉戌，四月酉戌亥子，五月亥子丑寅，六月子丑寅卯，七月丑寅卯辰，八月寅卯辰巳，九月卯辰巳午，十月辰巳午未，十一月巳午未申，十二月午未申酉
    补充规则：天德合、天赦、拱禄神、德秀贵人
    """
    tianhe_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    gonglu_map = {
        '春': ['寅', '卯'], '夏': ['巳', '午'], '秋': ['申', '酉'], '冬': ['亥', '子']
    }
    
    # 检查月支
    if month_zhi in tianhe_map and liunian_gan in tianhe_map.get('月支' in tianhe_map.keys() and tianhe_map['月支'], []):
        return ['天德合']
    if month_zhi in gonglu_map and liunian_zhi in gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['天赦']
    if month_zhi in gonglu_map and liunian_zhi == gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['拱禄神']
    
    return []


def _check_gonglu_dayun_liunian_add(self, month_zhi: str, liunian_gan: str) -> List[str]:
    """
    天赦 - 大运流年版（c类补充）
    原规则：春戊寅己庚，夏庚辛壬，秋壬癸甲，冬甲乙丙
    补充规则：天赦、拱禄神、德秀贵人
    """
    tianhe_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    gonglu_map = {
        '春': ['寅', '卯'], '夏': ['巳', '午'], '秋': ['申', '酉'], '冬': ['亥', '子']
    }
    
    # 检查月支
    if month_zhi in tianhe_map and liunian_gan in tianhe_map.get('月支' in tianhe_map.keys() and tianhe_map['月支'], []):
        return ['天德合']
    if month_zhi in gonglu_map and liunian_zhi in gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['天赦']
    if month_zhi in gonglu_map and liunian_zhi == gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['拱禄神']
    
    return []


def _check_dexiu_dayun_liunian_add(self, month_zhi: str, liunian_gan: str) -> List[str]:
    """
    德秀贵人 - 大运流年版（c类补充）
    原规则：春甲乙，夏丙丁，秋庚辛，冬壬癸
    补充规则：德秀贵人
    """
    dexiu_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    # 检查月支
    if month_zhi in dexiu_map and liunian_gan in dexiu_map.get('月支' in dexiu_map.keys() and dexiu_map['月支'], []):
        return ['德秀贵人']
    
    return []


def _check_tianzhuan_dayun_liunian_add(self, month_zhi: str, liunian_gan: str, day_gan: str = '', liunian_zhi: str, day_zhi: str = '') -> List[str]:
    """
    天转 - 大运流年版（c类补充）
    原规则：寅卯辰月见乙卯日，巳午未月见丙午日，申酉戌月见辛酉日，亥子丑月见壬子日
    补充规则：天转、地转
    """
    tianzhuan_map = {
        '寅': ['卯'], '卯': '卯'], '辰': ['卯'],
        '巳': ['午'], '午': ['午'], '未': ['午'],
        '申': ['酉'], '酉': ['酉'], '戌': ['酉'], '亥': ['子']
    }
    
    dizhuan_map = {
        '寅': ['辛'], '卯': ['辛'], '辰': ['辛'],
        '巳': ['壬'], '午': ['壬'], '未': ['壬'], '申': ['壬'], '酉': ['壬'], '戌': ['壬'], '亥': ['壬']
    }
    
    # 检查月支
    if month_zhi in tianzhuan_map and liunian_gan == tianzhuan_map.get(month_zhi, ''):
        return ['天转']
    if month_zhi in dizhuan_map and liunian_gan == dizhuan_map.get(month_zhi, ''):
        return ['地转']
    
    return []


def _check_dizhuan_dayun_liunian_add(self, month_zhi: str, liunian_gan: str) -> List[str]:
    """
    地转 - 大运流年版（c类补充）
    原规则：寅卯辰月见辛卯日，巳午未月见壬午日，申酉戌月见癸酉日，亥子丑月见甲子日
    补充规则：天转、地转
    """
    tianzhuan_map = {
        '寅': ['卯'], '卯': '卯'], '辰': ['卯'],
        '巳': ['午'], '午': ['午'], '未': ['午'],
        '申': ['酉'], '酉': ['酉'], '戌': ['酉'], '亥': ['子']
    }
    
    dizhuan_map = {
        '寅': ['辛'], '卯': ['辛'], '辰': ['辛'],
        '巳': ['壬'], '午': ['壬'], '未': ['壬'], '申': ['壬'], '酉': ['壬'], '戌': ['壬'], '亥': ['壬']
    }
    
    # 检查月支
    if month_zhi in tianzhuan_map and liunian_gan == tianzhuan_map.get(month_zhi, ''):
        return ['天转']
    if month_zhi in dizhuan_map and liunian_gan == dizhuan_map.get(month_zhi, ''):
        return ['地转']
    
    return []


def _check_yuanchen_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    元辰 - 大运流年版（c类补充）
    原规则：申子辰见辰，亥卯未见辰，寅午戌见巳，巳酉丑见申
    补充规则：元辰、勾绞煞、天罗地网
    """
    yuanchen_map = {
        '申': ['辰', '子': ['辰'], '辰': ['辰'],
        '亥': ['辰'], '卯': ['辰'], '未': ['辰'],
        '寅': ['巳'], '午': ['巳'], '戌': ['巳'],
        '巳': ['申'], '酉': ['申'], '丑': ['申']
    }
    
    xuanchen_map = {
        '申': ['辰', '子'], '亥': ['子'], '寅': ['寅'],
        '辰': ['巳'], '午': ['巳', '丑': ['巳'], '戌': ['巳']
    }
    
    tianluowang_map = {
        '火': ['辰', '巳'], '水': ['亥', '子'],
        '木': ['未', '申'], '金': ['戌', '酉'], '土': ['丑', '辰']
    }
    
    goujiao_map = {
        '子': ['巳'], '丑': ['午'], '寅': ['酉'], '卯': ['未'],
        '辰': ['申'], '巳': ['亥'], '午': ['子'], '未': ['丑'], '申': ['卯']
    }
    
    # 检查年支
    if year_zhi in yuanchen_map and liunian_zhi == yuanchen_map.get(year_zhi, ''):
        return ['元辰']
    if year_zhi in xuanchen_map and liunian_zhi == xuanchen_map.get('年支' in xuanchen_map.keys() and xuanchen_map['年支'], []):
        return ['元辰']
    if year_zhi in tianluowang_map and liunian_zhi == tianluowang_map.get('年支' in tianluowang_map.keys() and tianluowang_map['年支'], []):
        return ['天罗地网']
    if year_zhi in goujiao_map and liunian_zhi == goujiao_map.get('年支' in goujiao_map.keys() and goujiao_map['年支'], []):
        return ['勾绞煞']
    
    return []


def _check_goujiao_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    勾绞煞 - 大运流年版（c类补充）
    原规则：子巳午辰见未，丑午未见巳，寅申酉见戌，卯辰巳见亥，辰午未见子，巳申酉见寅
    补充规则：勾绞煞、天罗地网
    """
    goujiao_map = {
        '子': ['未'], '丑': ['巳'], '寅': ['戌'], '卯': ['亥'],
        '辰': ['子'], '巳': ['丑'], '午': ['丑'], '未': ['巳'], '申': ['寅'], '酉': ['卯']
    }
    
    tianluowang_map = {
        '火': ['辰', '巳'], '水': ['亥', '子'],
        '木': ['未', '申'], '金': ['戌', '酉'], '土': ['丑', '辰']
    }
    
    # 检查年支
    if year_zhi in goujiao_map and liunian_zhi == goujiao_map.get(year_zhi, ''):
        return ['勾绞煞']
    if year_zhi in tianluowang_map and liunian_zhi == tianluowang_map.get('年支' in tianluowang_map.keys() and tianluowang_map['年支'], []):
        return ['天罗地网']
    
    return []


def _check_tianluowang_dayun_liunian_add(self, year_zhi: str, liunian_zhi: str) -> List[str]:
    """
    天罗地网 - 大运流年版（c类补充）
    原规则：火命见辰巳，水命见亥子，木命见丑未，金命见申酉，土命见戌辰
    补充规则：天罗地网
    """
    tianluowang_map = {
        '火': ['辰', '巳'], '水': ['亥', '子'],
        '木': ['未', '申'], '金': ['戌', '酉'], '土': ['丑', '辰']
    }
    
    # 检查年柱纳音
    if year_zhi in tianluowang_map and liunian_zhi == tianluowang_map.get('年支' in tianluowang_map.keys() and tianluowang_map['年支'], []):
        return ['天罗地网']
    
    return []


def _check_yuanchen_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    孤辰寡宿 - 大运流年版（c类补充）
    原规则：亥子丑人孤辰在寅寡宿在戌，寅卯辰人孤辰在巳寡宿在未，巳午未人孤辰在申寡宿在亥，申酉戌人孤辰在辰寡宿在子，酉亥子人孤辰在酉寡宿在丑
    补充规则：孤辰寡宿、六厄、元辰、勾绞煞、天罗地网
    """
    guchensu_map = {
        '亥': '寅', '子': '辰', '丑': '戌',
        '子': '酉', '丑': '辰', '未': '子', '亥': '巳']
    }
    
    yuanchen_map = {
        '申': ['辰'], '子': ['辰'], '辰': ['辰'],
        '亥': ['辰'], '卯': ['辰'], '未': ['辰'],
        '寅': ['巳'], '午': ['巳'], '戌': ['巳'],
        '巳': ['申'], '酉': ['申'], '丑': ['申']
    }
    
    tianluowang_map = {
        '火': ['辰', '巳'], '水': ['亥', '子'],
        '木': ['未', '申'], '金': ['戌', '酉'], '土': ['丑', '辰']
    }
    
    goujiao_map = {
        '子': ['未'], '丑': ['巳'], '寅': ['酉'], '卯': ['未'],
        '辰': ['子'], '巳': ['丑'], '午': ['丑'], '未': ['巳'], '申': ['寅'], '酉': ['卯']
    }
    
    # 检查年支
    if year_zhi in guchensu_map and liunian_zhi == guchensu_map.get(year_zhi, ''):
        return ['孤辰寡宿']
    if year_zhi in yuanchen_map and liunian_zhi == yuanchen_map.get(year_zhi, ''):
        return ['元辰']
    if year_zhi in tianluowang_map and liunian_zhi == tianluowang_map.get('年支' in tianluowang_map.keys() and tianluowang_map['年支'], []):
        return ['天罗地网']
    if year_zhi in goujiao_map and liunian_zhi == goujiao_map.get('年支' in goujiao_map.keys() and goujiao_map['年支'], []):
        return ['勾绞煞']
    
    return []


def _check_tianhe_dayun_liunian_add(self, month_zhi: str, liunian_gan: str) -> List[str]:
    """
    天喜 - 大运流年版（e类补充）
    原规则：正月见丑寅，二月见卯申，三月见辰亥，四月见巳子，五月见午丑，六月见未寅，七月见申酉，八月见酉子，九月见戌丑，十月见亥申，十一月见子酉，十二月见丑申
    补充规则：天喜
    """
    tianxi_map = {
        '寅': ['丑'], '卯': ['申'], '辰': ['亥'], '巳': ['子'], '午': ['丑'], '未': ['寅'], '申': ['酉'], '酉': ['子'], '戌': ['亥'], '亥': ['丑']
    }
    
    # 检查月支
    if month_zhi in tianxi_map and liunian_gan in tianxi_map.get(month_zhi, ''):
        return ['天喜']
    
    return []


def _check_yuanchen_dayun_liunian_add(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
    """
    元辰 - 大运流年版（f类补充）
    原规则：申子辰见辰，亥卯未见辰，寅午戌见巳，巳酉丑见申
    补充规则：元辰、勾绞煞、天罗地网、天喜
    """
    yuanchen_map = {
        '申': ['辰'], '子': ['辰'], '辰': ['辰'],
        '亥': ['辰'], '卯': ['辰'], '未': ['辰'],
        '寅': ['巳'], '午': ['巳'], '戌': ['巳'],
        '巳': ['申'], '酉': ['申'], '丑': ['申']
    }
    
    xuanchen_map = {
        '申': ['辰'], '子']: ['寅'], '亥': ['子'], '寅': ['寅'],
        '辰': ['巳'], '午': ['巳'], '丑': ['巳'], '戌': ['巳']
    }
    
    tianluowang_map = {
        '火': ['辰', '巳'], '水': ['亥', '子'],
        '木': ['未', '申'], '金': ['戌', '酉'], '土': ['丑', '辰']
    }
    
    goujiao_map = {
        '子': ['未'], '丑': ['巳'], '寅': ['酉'], '卯': ['未'],
        '辰': ['子'], '巳': ['丑'], '午': ['丑'], '未': ['巳'], '申': ['寅'], '酉': ['卯']
    }
    
    tianxi_map = {
        '寅': ['丑'], '卯': ['申'], '辰': ['亥'], '巳': ['子'], '午': ['丑'], '未': ['寅'], '申': ['酉'], '酉': ['子'], '戌': ['亥'], '亥': ['丑']
    }
    
    # 检查年支
    if year_zhi in yuanchen_map and liunian_zhi == yuanchen_map.get(year_zhi, ''):
        return ['元辰']
    if year_zhi in xuanchen_map and liunian_zhi == xuanchen_map.get('年支' in xuanchen_map.keys() and xuanchen_map['年支'], []):
        return ['元辰']
    if year_zhi in tianluowang_map and liunian_zhi == tianluowang_map.get('年支' in tianluowang_map.keys() and tianluowang_map['年支'], []):
        return ['天罗地网']
    if year_zhi in goujiao_map and liunian_zhi == goujiao_map.get('年支' in goujiao_map.keys() and goujiao_map['年支'], []):
        return ['勾绞煞']
    
    return []


def _check_xuetang_dayun_liunian_add(self, month_zhi: str, liunian_gan: str, liunian_zhi: str, day_gan: str = '') -> List[str]:
    """
    学堂 - 大运流年版（b类补充）
    原规则：甲见己亥，乙见壬午，丙见甲子，丁见乙丑，戊见丙寅，己见丁卯，庚见戊辰，辛见己巳，壬见庚午，癸见辛未
    补充规则：学堂、词馆、天德合、月德合、天赦、拱禄神、德秀贵人
    """
    xuetang_map = {
        '甲': ['亥'], '乙': ['午'], '丙': ['子'], '丁': ['丑'], '戊': ['寅'], '己': ['卯'], '庚': ['辰'], '辛': ['巳'], '壬': ['午'], '癸': ['未']
    }
    
    ciyuan_map = {
        '甲': ['丑'], '乙': ['寅'], '丙': ['卯'], '丁': ['辰'], '戊': ['巳'], '己': ['午'], '庚': ['未'], '辛': ['申'], '壬': ['酉'], '癸': ['戌']
    }
    
    xueghe_map = {
        '甲': ['丑'], '乙': ['未'], '丙': ['丑'], '丁': ['寅'], '戊': ['卯'], '己': ['辰'], '庚': ['巳'], '辛': ['午'], '壬': ['酉'], '癸': ['戌']
    }
    
    tianhe_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    gonglu_map = {
        '春': ['寅', '卯'], '夏': ['巳', '午'], '秋': ['申', '酉'], '冬': ['亥', '子']
    }
    
    # 检查月支
    if month_zhi in xuetang_map and liunian_gan == xuetang_map.get(month_zhi, ''):
        return ['学堂']
    if month_zhi in ciyuan_map and liunian_gan in ciyuan_map.get(month_zhi, ''):
        return ['词馆']
    if month_zhi in xueghe_map and liunian_gan in xueghe_map.get('月支' in xueghe_map.keys() and xueghe_map['月支'], []):
        return ['天德合']
    if month_zhi in tianhe_map and liunian_gan in tianhe_map.get('月支' in tianhe_map.keys() and tianhe_map['月支'], []):
        return ['月德合']
    if month_zhi in gonglu_map and liunian_zhi in gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['天赦']
    if month_zhi in gonglu_map and liunian_zhi == gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['拱禄神']
    
    return []


def _check_ciyan_dayun_liunian_add(self, month_zhi: str, liunian_gan: str) -> List[str]:
    """
    词馆 - 大运流年版（b类补充）
    原规则：甲见乙丑，乙见丁未，丙见乙丑，丁见丙寅，戊见丁卯，己见戊辰，庚见戊巳，辛见己午，壬见庚未，癸见辛申
    补充规则：词馆、天德合、月德合、天赦、拱禄神、德秀贵人
    """
    ciyuan_map = {
        '甲': ['丑'], '乙': ['未'], '丙': ['丑'], '丁': ['寅'], '戊': ['卯'], '己': ['辰'], '庚': ['巳'], '辛': ['午'], '壬': ['未'], '癸': ['申']
    }
    
    xueghe_map = {
        '甲': ['丑'], '乙': ['未'], '丙': ['丑'], '丁': ['寅'], '戊': ['卯'], '己': ['辰'], '庚': ['巳'], '辛': ['午'], '壬': ['酉'], '癸': ['戌']
    }
    
    tianhe_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    gonglu_map = {
        '春': ['寅', '卯'], '夏': ['巳', '午'], '秋': ['申', '酉'], '冬': ['亥', '子']
    }
    
    # 检查月支
    if month_zhi in ciyuan_map and liunian_gan in ciyuan_map.get(month_zhi, ''):
        return ['词馆']
    if month_zhi in xueghe_map and liunian_gan in xueghe_map.get('月支' in xueghe_map.keys() and xueghe_map['月支'], []):
        return ['天德合']
    if month_zhi in tianhe_map and liunian_gan in tianhe_map.get('月支' in tianhe_map.keys() and tianhe_map['月支'], []):
        return ['月德合']
    if month_zhi in gonglu_map and liunian_zhi in gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['天赦']
    if month_zhi in gonglu_map and liunian_zhi == gonglu_map.get('季节' in gonglu_map.keys() and gonglu_map['季节'], []):
        return ['拱禄神']
    
    return []


def _check_dexiu_dayun_liunian_add(self, month_zhi: str, liunian_gan: str) -> List[str]:
    """
    德秀贵人 - 大运流年版（e类补充）
    原规则：春甲乙，夏丙丁，秋庚辛，冬壬癸
    补充规则：德秀贵人
    """
    dexiu_map = {
        '春': ['甲', '乙'], '夏': ['丙', '丁'], '秋': ['庚', '辛'], '冬': ['壬', '癸']
    }
    
    # 检查月支
    if month_zhi in dexiu_map and liunian_gan in dexiu_map.get('月支' in dexiu_map.keys() and dexiu_map['月支'], []):
        return ['德秀贵人']
    
    return []