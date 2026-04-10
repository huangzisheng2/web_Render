#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神煞数据库系统
用于八字四柱神煞的自动识别和分析

作者: Claude AI
创建日期: 2025-01-30
版本: 1.0
"""

from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict, namedtuple
import json


class ShenShaInfo:
    """神煞信息类,存储单个神煞的完整属性"""
    
    def __init__(self, name: str, category: str, definition: str, 
                 preference: str, condition: str, explanation: str, source: str):
        """
        初始化神煞信息
        
        参数:
            name: 神煞名称
            category: 类别(吉神/凶煞)
            definition: 定义说明
            preference: 喜忌(喜见/忌见/喜忌参半)
            condition: 形成条件口诀或规则
            explanation: 凶吉说明及古籍依据
            source: 古籍依据
        """
        self.name = name
        self.category = category
        self.definition = definition
        self.preference = preference
        self.condition = condition
        self.explanation = explanation
        self.source = source
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'name': self.name,
            'category': self.category,
            'definition': self.definition,
            'preference': self.preference,
            'condition': self.condition,
            'explanation': self.explanation,
            'source': self.source
        }


class ShenShaDatabase:
    """神煞数据库类,存储所有神煞的计算规则和属性"""
    
    # 天干列表
    GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    
    # 地支列表
    ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    # 月份对应的地支
    MONTH_ZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']
    
    # 纳音五行
    NAYIN = {
        ('甲', '子'): '海中金', ('乙', '丑'): '海中金',
        ('丙', '寅'): '炉中火', ('丁', '卯'): '炉中火',
        ('戊', '辰'): '大林木', ('己', '巳'): '大林木',
        ('庚', '午'): '路旁土', ('辛', '未'): '路旁土',
        ('壬', '申'): '剑锋金', ('癸', '酉'): '剑锋金',
        ('甲', '戌'): '山头火', ('乙', '亥'): '山头火',
        ('丙', '子'): '涧下水', ('丁', '丑'): '涧下水',
        ('戊', '寅'): '城头土', ('己', '卯'): '城头土',
        ('庚', '辰'): '白蜡金', ('辛', '巳'): '白蜡金',
        ('壬', '午'): '杨柳木', ('癸', '未'): '杨柳木',
        ('甲', '申'): '井泉水', ('乙', '酉'): '井泉水',
        ('丙', '戌'): '屋上土', ('丁', '亥'): '屋上土',
        ('戊', '子'): '霹雳火', ('己', '丑'): '霹雳火',
        ('庚', '寅'): '松柏木', ('辛', '卯'): '松柏木',
        ('壬', '辰'): '长流水', ('癸', '巳'): '长流水',
        ('甲', '午'): '砂中金', ('乙', '未'): '砂中金',
        ('丙', '申'): '山下火', ('丁', '酉'): '山下火',
        ('戊', '戌'): '平地木', ('己', '亥'): '平地木',
        ('庚', '子'): '壁上土', ('辛', '丑'): '壁上土',
        ('壬', '寅'): '金泊金', ('癸', '卯'): '金泊金',
        ('甲', '辰'): '覆灯火', ('乙', '巳'): '覆灯火',
        ('丙', '午'): '天河水', ('丁', '未'): '天河水',
        ('戊', '申'): '大驿土', ('己', '酉'): '大驿土',
        ('庚', '戌'): '钗钏金', ('辛', '亥'): '钗钏金',
        ('壬', '子'): '桑柘木', ('癸', '丑'): '桑柘木',
        ('甲', '寅'): '大溪水', ('乙', '卯'): '大溪水',
        ('丙', '辰'): '砂中土', ('丁', '巳'): '砂中土',
        ('戊', '午'): '天上火', ('己', '未'): '天上火',
        ('庚', '申'): '石榴木', ('辛', '酉'): '石榴木',
        ('壬', '戌'): '大海水', ('癸', '亥'): '大海水',
    }
    
    # 六十甲子旬空亡
    XUN_KONG = {
        ('甲', '子'): ('戌', '亥'), ('乙', '丑'): ('戌', '亥'),
        ('丙', '寅'): ('戌', '亥'), ('丁', '卯'): ('戌', '亥'),
        ('戊', '辰'): ('戌', '亥'), ('己', '巳'): ('戌', '亥'),
        ('庚', '午'): ('戌', '亥'), ('辛', '未'): ('戌', '亥'),
        ('壬', '申'): ('戌', '亥'), ('癸', '酉'): ('戌', '亥'),
        ('甲', '戌'): ('申', '酉'), ('乙', '亥'): ('申', '酉'),
        ('丙', '子'): ('申', '酉'), ('丁', '丑'): ('申', '酉'),
        ('戊', '寅'): ('申', '酉'), ('己', '卯'): ('申', '酉'),
        ('庚', '辰'): ('申', '酉'), ('辛', '巳'): ('申', '酉'),
        ('壬', '午'): ('申', '酉'), ('癸', '未'): ('申', '酉'),
        ('甲', '申'): ('午', '未'), ('乙', '酉'): ('午', '未'),
        ('丙', '戌'): ('午', '未'), ('丁', '亥'): ('午', '未'),
        ('戊', '子'): ('午', '未'), ('己', '丑'): ('午', '未'),
        ('庚', '寅'): ('午', '未'), ('辛', '卯'): ('午', '未'),
        ('壬', '辰'): ('午', '未'), ('癸', '巳'): ('午', '未'),
        ('甲', '午'): ('辰', '巳'), ('乙', '未'): ('辰', '巳'),
        ('丙', '申'): ('辰', '巳'), ('丁', '酉'): ('辰', '巳'),
        ('戊', '戌'): ('辰', '巳'), ('己', '亥'): ('辰', '巳'),
        ('庚', '子'): ('辰', '巳'), ('辛', '丑'): ('辰', '巳'),
        ('壬', '寅'): ('辰', '巳'), ('癸', '卯'): ('辰', '巳'),
    }
    
    def __init__(self):
        """初始化神煞数据库"""
        self._shensha_dict: Dict[str, ShenShaInfo] = {}
        self._init_shensha_data()
    
    def _init_shensha_data(self):
        """初始化所有神煞数据"""
        
        # ============ 吉神 ============
        
        # 天乙贵人
        self._add_shensha(
            name='天乙贵人',
            category='吉神',
            definition='最尊贵吉神，主聪明智慧、遇难呈祥',
            preference='喜见（宜旺相，忌冲克）',
            condition='甲戊庚牛羊（丑未），乙己鼠猴乡（子申），丙丁猪鸡位（亥酉），壬癸兔蛇藏（卯巳），六辛逢马虎（寅午）',
            explanation='大吉。天乙者，天上之神，在紫微垣阖门外……主聪明智慧，出入近贵，功名早达。',
            source='《渊海子平·论贵神优劣》'
        )
        
        # 太极贵人
        self._add_shensha(
            name='太极贵人',
            category='吉神',
            definition='主学术、技艺成就，悟性高',
            preference='喜见（宜配印星）',
            condition='甲乙生人子午中，丙丁鸡兔定亨通；戊己两干临四季，庚辛寅亥禄丰隆；壬癸巳申偏喜美，值此应当福气钟',
            explanation='吉。太极者，太初也，始也……主聪明好学，喜神秘事物，得之则术业精通。',
            source='《渊海子平·论太极贵人》'
        )
        
        # 文昌贵人
        self._add_shensha(
            name='文昌贵人',
            category='吉神',
            definition='主文才、考试运、文书利',
            preference='喜见（宜食伤生旺）',
            condition='甲乙巳午报君知，丙戊申宫丁己鸡；庚猪辛鼠壬逢虎，癸人见卯入云梯',
            explanation='吉。文昌者，食神之临官所在……主文章盖世，科甲有名，登科及第。',
            source='《渊海子平·论文昌》'
        )
        
        # 天德贵人
        self._add_shensha(
            name='天德贵人',
            category='吉神',
            definition='化解凶煞第一吉神，主仁慈、逢凶化吉',
            preference='喜见（尤忌冲克，合则力减）',
            condition='正月丁，二月申，三月壬，四月辛，五月亥，六月甲，七月癸，八月寅，九月丙，十月乙，十一月巳，十二月庚',
            explanation='大吉。天德者，五行福德之辰……所至之处，一切凶煞隐伏，主一生无险，仁厚好施。',
            source='《渊海子平·论天德》'
        )
        
        # 月德贵人
        self._add_shensha(
            name='月德贵人',
            category='吉神',
            definition='类似天德，主温和、福泽深厚',
            preference='喜见（宜配天德更佳）',
            condition='寅午戌月丙，亥卯未月甲，申子辰月壬，巳酉丑月庚',
            explanation='大吉。月德者，阴德也……其功与天德同，主福寿康宁，妇人尤吉。',
            source='《渊海子平·论月德》'
        )
        
        # 三奇贵人
        self._add_shensha(
            name='三奇贵人',
            category='吉神',
            definition='天地人三奇（乙丙丁、甲戊庚、壬癸辛），主非凡成就',
            preference='喜见（需顺排，忌倒乱）',
            condition='乙丙丁（天上三奇）：日干乙，月干丙，时干丁（顺排）；甲戊庚、壬癸辛同理（干支顺布为贵）',
            explanation='大吉。凡命遇三奇，主人精神异常，襟怀卓越，好奇尚大，博学多能，贵显可期。',
            source='《渊海子平·论三奇》'
        )
        
        # 华盖
        self._add_shensha(
            name='华盖',
            category='吉神',
            definition='主艺术、宗教缘分，亦主孤独',
            preference='喜忌参半（吉则艺精，凶则孤僻）',
            condition='寅午戌见戌，亥卯未见未，申子辰见辰，巳酉丑见丑',
            explanation='中性。华盖者，黄帝之车盖也……主孤高，有科名、文章、僧道之兆，逢空亡则遁入空门。',
            source='《渊海子平·论华盖》'
        )
        
        # 将星
        self._add_shensha(
            name='将星',
            category='吉神',
            definition='主领导力、权威、统帅之才',
            preference='喜见（宜掌权，忌弱囚）',
            condition='寅午戌见午，亥卯未见卯，申子辰见子，巳酉丑见酉',
            explanation='吉。将星者，如大将驻军……主统兵威重，武略出众，文职掌权亦吉。',
            source='《渊海子平·论将星》'
        )
        
        # 驿马
        self._add_shensha(
            name='驿马',
            category='吉神',
            definition='主动态、奔波、机遇（动则发，静则滞）',
            preference='喜忌参半（经商、外交喜见）',
            condition='申子辰马在寅，寅午戌马在申，亥卯未马在巳，巳酉丑马在亥',
            explanation='中性。马者，禄命之驰骤……主迁动、远行、升迁、经商获利，忌冲克则奔波劳碌。',
            source='《渊海子平·论驿马》'
        )
        
        # 金舆
        self._add_shensha(
            name='金舆',
            category='吉神',
            definition='主富贵、车驾之象，象征身份尊贵',
            preference='喜见（宜配官星）',
            condition='甲干见辰、乙干见巳、丙干见未、戊干见未、丁干见申、己干见申、庚干见戌、辛干见亥、壬干见丑、癸干见寅（以年干、日干查四柱地支）',
            explanation='吉。金舆者，华丽之车……主富贵双全，乘马坐车之荣，妇人逢之多嫁贵夫。',
            source='《渊海子平·论金舆》'
        )
        
        # 天赦
        self._add_shensha(
            name='天赦',
            category='吉神',
            definition='化解刑冲之吉神，主宽恕、赦免',
            preference='喜见（尤忌凶煞重叠）',
            condition='春戊寅，夏甲午，秋戊申，冬甲子',
            explanation='吉。天赦者，赦过宥罪之辰……命中逢之，主一生少官非口舌，逢凶化吉。',
            source='《渊海子平·论天赦》'
        )
        
        # 福星贵人
        self._add_shensha(
            name='福星贵人',
            category='吉神',
            definition='主福气、安逸、衣食丰足',
            preference='喜见（宜身旺）',
            condition='甲干见寅子、丙干见寅子、乙干见卯丑、癸干见卯丑、戊干见申、己干见未、丁干见亥、庚干见午、辛干见巳、壬干见辰（以年干、日干查四柱地支）',
            explanation='吉。福星者，福气之星……主平生安享福禄，衣食丰盈，无忧无虑。',
            source='《渊海子平·论福星贵人》'
        )
        
        # 国印贵人
        self._add_shensha(
            name='国印贵人',
            category='吉神',
            definition='主权柄、印章、公职（如官员、律师）',
            preference='喜见（宜官杀旺）',
            condition='甲见戌，乙见亥，丙见丑，丁见寅，戊见丑，己见寅，庚见辰，辛见巳，壬见未，癸见申',
            explanation='吉。国印者，朝廷之印信……主秉节持权，为官掌印，文职显达。',
            source='《渊海子平·论国印贵人》'
        )
        
        # 学堂
        self._add_shensha(
            name='学堂',
            category='吉神',
            definition='主学业、读书天赋',
            preference='喜见（宜配印星）',
            condition='甲见己亥，乙见壬午，丙见丙寅，丁见丁酉，戊见戊寅，己见己酉，庚见辛巳，辛见甲子，壬见甲申，癸见乙卯',
            explanation='吉。学堂者，读书之舍……主聪明好学，文章出众，科举有望。',
            source='《渊海子平·论学堂》'
        )
        
        # 词馆
        self._add_shensha(
            name='词馆',
            category='吉神',
            definition='主文采、著述能力（比学堂更高一级）',
            preference='喜见（宜配食伤）',
            condition='甲见庚寅，乙见辛卯，丙见乙巳，丁见戊午，戊见丁巳，己见庚午，庚见壬申，辛见癸酉，壬见癸亥，癸见壬戌',
            explanation='吉。词馆者，作文之馆……主文采飞扬，著述立说，文人学士之征。',
            source='《渊海子平·论词馆》'
        )
        
        # 德秀贵人
        self._add_shensha(
            name='德秀贵人',
            category='吉神',
            definition='主才华、德行出众（德指天德月德，秀指伤官食神）',
            preference='喜见（宜身旺）',
            condition='寅午戌月丙丁为德戊癸为秀，申子辰月壬癸戊己为德丙辛甲为秀，巳酉丑月庚辛为德乙庚为秀，亥卯未月甲乙为德丁壬为秀',
            explanation='吉。德秀者，德者天月二德，秀者伤官食神……主才德兼备，文章秀拔，贵人提携。',
            source='《渊海子平·论德秀贵人》'
        )
        
        # 天医
        self._add_shensha(
            name='天医',
            category='吉神',
            definition='主医术、健康（宜为医生、护士）',
            preference='喜见（忌冲克）',
            condition='正月生见丑，二月生见寅，三月生见卯，四月生见辰，五月生见巳，六月生见午，七月生见未，八月生见申，九月生见酉，十月生见戌，十一月生见亥，十二月生见子',
            explanation='吉。天医者，司医之星……主疗疾愈病，身康体健，宜从医者佳。',
            source='《渊海子平·论天医》'
        )
        
        # 魁罡
        self._add_shensha(
            name='魁罡',
            category='吉神',
            definition='主刚健果断、权威（亦主刑克）',
            preference='喜忌参半（身强喜，身弱忌）',
            condition='日柱为：壬辰、庚辰、戊戌、庚戌',
            explanation='偏吉（身强吉，身弱凶）。魁罡者，天罡地魁……主性急刚烈，掌权立事，然克妻刑子，身弱遇之贫夭。',
            source='《渊海子平·论魁罡》'
        )
        
        # ============ 凶煞 ============
        
        # 羊刃
        self._add_shensha(
            name='羊刃',
            category='凶煞',
            definition='阳干帝旺之地（甲见卯，丙戊见午等），主刚暴、血光',
            preference='忌见（需制化，如官杀制刃）',
            condition='甲日卯，乙日寅，丙日午，丁日巳，戊日午，己日巳，庚日酉，辛日申，壬日子，癸日亥',
            explanation='凶。羊刃者，禄前一位……主性急凶暴，易遭刀兵、血光、破财，女命克夫。',
            source='《渊海子平·论羊刃》'
        )
        
        # 劫煞
        self._add_shensha(
            name='劫煞',
            category='凶煞',
            definition='主争夺、破耗、盗贼',
            preference='忌见（尤忌冲合）',
            condition='申子辰见巳，亥卯未见申，寅午戌见亥，巳酉丑见寅',
            explanation='凶。劫者，夺也……主破财、争斗、盗贼之患，岁运逢之尤甚。',
            source='《渊海子平·论劫煞》'
        )
        
        # 灾煞
        self._add_shensha(
            name='灾煞',
            category='凶煞',
            definition='主灾病、意外（劫煞对冲位）',
            preference='忌见（尤忌叠见）',
            condition='劫煞对冲位：申子辰劫煞在巳→灾煞在午；亥卯未劫煞在申→灾煞在酉；寅午戌劫煞在亥→灾煞在子；巳酉丑劫煞在寅→灾煞在卯',
            explanation='凶。灾煞者，其性勇猛……主血光、牢狱、疾病之灾，又名"白虎煞"。',
            source='《渊海子平·论灾煞》'
        )
        
        # 天罗地网
        self._add_shensha(
            name='天罗地网',
            category='凶煞',
            definition='主困顿、束缚（火命见戌亥为天罗，水命见辰巳为地网）',
            preference='忌见（尤忌重叠）',
            condition='天罗：年柱纳音火（丙丁巳午），见戌亥；地网：年柱纳音水（壬癸亥子），见辰巳',
            explanation='凶。男怕天罗，女怕地网……主刑罚、牢狱、困顿不前，岁运逢之加重。',
            source='《渊海子平·论天罗地网》'
        )
        
        # 空亡
        self._add_shensha(
            name='空亡',
            category='凶煞',
            definition='旬中空亡之地（甲子旬戌亥空），主虚浮、不实',
            preference='忌见（吉神落空减吉，凶煞落空减凶）',
            condition='六十甲子每旬剩余两支为空亡（如甲子旬戌亥空，甲戌旬申酉空）',
            explanation='中性偏凶。空亡者，真空亡也……吉神落空则吉减，凶煞落空则凶散，凡事皆虚。',
            source='《渊海子平·论空亡》'
        )
        
        # 十恶大败
        self._add_shensha(
            name='十恶大败',
            category='凶煞',
            definition='禄逢空亡之日，主钱财耗散',
            preference='忌见（忌经商、理财）',
            condition='甲辰、乙巳、壬申、丙申、丁亥、庚辰、戊戌、癸亥、辛巳、己丑',
            explanation='凶。十恶者，凶败之极……主仓库金银化为灰尘，一生财来财去。',
            source='《渊海子平·论十恶大败》'
        )
        
        # 桃花（原咸池）
        self._add_shensha(
            name='桃花',
            category='凶煞',
            definition='主异性缘、风流（墙外桃花更凶）',
            preference='忌见（尤忌女命墙外桃花）',
            condition='寅午戌见卯，亥卯未见子，申子辰见酉，巳酉丑见午',
            explanation='中性偏凶。桃花者，咸池也……主奸邪淫鄙，女子尤忌，墙外桃花主私奔。',
            source='《渊海子平·论咸池》'
        )
        
        # 孤辰寡宿
        self._add_shensha(
            name='孤辰寡宿',
            category='凶煞',
            definition='主孤独、婚姻不顺（男怕孤辰，女怕寡宿）',
            preference='忌见（尤忌夫妻宫见）',
            condition='亥子丑人，孤辰在寅，寡宿在戌；寅卯辰人，孤辰在巳，寡宿在丑；巳午未人，孤辰在申，寡宿在辰；申酉戌人，孤辰在亥，寡宿在未',
            explanation='凶。孤辰寡宿……主孤独无依，婚姻难就，六亲冷淡。',
            source='《渊海子平·论孤辰寡宿》'
        )
        
        # 元辰（大耗）
        self._add_shensha(
            name='元辰',
            category='凶煞',
            definition='主破财、是非、意外',
            preference='忌见（尤忌冲合）',
            condition='阳男阴女：年支顺数前一位（子→丑，丑→寅）；阴男阳女：年支逆数前一位（子→亥，亥→戌）',
            explanation='凶。元辰者，大耗也……主官事、破财、不测之灾，又名"毛头星"。',
            source='《渊海子平·论元辰》'
        )
        
        # 六厄
        self._add_shensha(
            name='六厄',
            category='凶煞',
            definition='主困顿、阻碍（剥官之煞）',
            preference='忌见（尤忌官星遇之）',
            condition='申子辰见卯，亥卯未见午，寅午戌见酉，巳酉丑见子',
            explanation='凶。六厄者，剥官之煞……主仕途阻滞，事业难成，升迁受阻。',
            source='《渊海子平·论六厄》'
        )
        
        # 勾绞煞
        self._add_shensha(
            name='勾绞煞',
            category='凶煞',
            definition='主是非、口舌、牵连',
            preference='忌见（尤忌岁运逢之）',
            condition='阳男阴女，命前三辰为勾，命后三辰为绞；阴男阳女，命前三辰为绞，命后三辰为勾',
            explanation='凶。勾者牵连，绞者羁绊……主官非口舌，牵连受害，婚姻不利。',
            source='《渊海子平·论勾绞》'
        )
        
        # 孤鸾煞
        self._add_shensha(
            name='孤鸾煞',
            category='凶煞',
            definition='主婚姻不顺、夫缘薄（女命尤忌）',
            preference='忌见（日柱或时柱见）',
            condition='乙巳、丁巳、辛亥、戊申、甲寅、丙午、戊午、壬子',
            explanation='凶。孤鸾者，主夫绝嗣……主婚姻不顺，夫缘浅薄，或守寡孤独。',
            source='《渊海子平·论孤鸾》'
        )
        
        # 阴阳差错
        self._add_shensha(
            name='阴阳差错',
            category='凶煞',
            definition='主婚姻差错、夫妻不和',
            preference='忌见（日柱或时柱见）',
            condition='丙子、丁丑、戊寅、辛卯、壬辰、癸巳、丙午、丁未、戊申、辛酉、壬戌、癸亥',
            explanation='凶。阴阳差者，夫妇不和……主夫妻反目，家宅不宁，再婚之兆。',
            source='《渊海子平·论阴阳差错》'
        )
        
        # 亡神
        self._add_shensha(
            name='亡神',
            category='凶煞',
            definition='主是非、心机深、破财',
            preference='忌见（尤忌官杀弱）',
            condition='申子辰见亥，亥卯未见寅，寅午戌见巳，巳酉丑见申',
            explanation='凶。亡神者，亡身失意……主心机深沉，是非口舌，破财耗资。',
            source='《渊海子平·论亡神》'
        )
        
        # 六害（六穿）
        self._add_shensha(
            name='六害',
            category='凶煞',
            definition='主不和、伤害、分离（如子未害、丑午害等）',
            preference='忌见（尤忌夫妻宫见）',
            condition='子未、丑午、寅巳、卯辰、申亥、酉戌',
            explanation='凶。害者，损也……主六亲不睦，夫妻反目，骨肉分离。',
            source='《渊海子平·论六害》'
        )
        
        # 披麻
        self._add_shensha(
            name='披麻',
            category='凶煞',
            definition='主丧事、孝服（主本人或近亲有丧）',
            preference='忌见（岁运逢之主孝期）',
            condition='子年见酉，丑年见戌，寅年见亥，卯年见子，辰年见丑，巳年见寅，午年见卯，未年见辰，申年见巳，酉年见午，戌年见未，亥年见申',
            explanation='凶。披麻者，孝服之煞……主丧事临门，披麻戴孝，近亲有灾。',
            source='《渊海子平·论披麻》'
        )
        
        # 丧门
        self._add_shensha(
            name='丧门',
            category='凶煞',
            definition='主凶灾、丧事（与吊客配对）',
            preference='忌见（岁运逢之主凶）',
            condition='子年见寅，丑年见卯，寅年见辰，卯年见巳，辰年见午，巳年见未，午年见申，未年见酉，申年见戌，酉年见亥，戌年见子，亥年见丑',
            explanation='凶。丧门者，主丧亡……主凶灾横祸，疾病死亡，岁运逢之主孝服。',
            source='《渊海子平·论丧门》'
        )
        
        # 吊客
        self._add_shensha(
            name='吊客',
            category='凶煞',
            definition='主吊唁、孝服（与丧门配对）',
            preference='忌见（岁运逢之主孝）',
            condition='子年见戌，丑年见亥，寅年见子，卯年见丑，辰年见寅，巳年见卯，午年见辰，未年见巳，申年见午，酉年见未，戌年见申，亥年见酉',
            explanation='凶。吊客者，主吊唁……主有吊丧之事，近亲疾病，岁运逢之主孝服。',
            source='《渊海子平·论吊客》'
        )
        
        # 白虎
        self._add_shensha(
            name='白虎',
            category='凶煞',
            definition='主血光、刑伤、横祸（与丧门吊客同属岁煞）',
            preference='忌见（岁运逢之主血光）',
            condition='子年见午，丑年见未，寅年见申，卯年见酉，辰年见戌，巳年见亥，午年见子，未年见丑，申年见寅，酉年见卯，戌年见辰，亥年见巳',
            explanation='凶。白虎者，西方金神……主血光、刑伤、横祸，孕妇逢之防产难。',
            source='《渊海子平·论白虎》'
        )
        
        # 天狗
        self._add_shensha(
            name='天狗',
            category='凶煞',
            definition='主损伤、破相、小人口舌',
            preference='忌见（岁运逢之主损）',
            condition='子年见丑，丑年见寅，寅年见卯，卯年见辰，辰年见巳，巳年见午，午年见未，未年见申，申年见酉，酉年见戌，戌年见亥，亥年见子',
            explanation='凶。天狗者，主损伤……主破相、手术、小人暗算，儿童逢之防惊吓。',
            source='《渊海子平·论天狗》'
        )

        # ============ 新增神煞 ============

        # 天德合
        self._add_shensha(
            name='天德合',
            category='吉神',
            definition='天德所在天干的正五合，德神之辅，增强天德之力',
            preference='喜见（与天德同现、生助用神；忌被冲克、空亡）',
            condition='天德天干五合（丁→壬，申→巳，壬→丁，辛→丙，亥→寅，甲→己，癸→戊，寅→亥，丙→辛，乙→庚，巳→申，庚→乙）',
            explanation='吉。《神煞赋》："天德合，福加倍。"辅助天德解厄，主贵人暗助。',
            source='《神煞赋》'
        )

        # 月德合
        self._add_shensha(
            name='月德合',
            category='吉神',
            definition='月德所在天干的正五合，德神之辅，增强月德之力',
            preference='喜见（与月德同现、生助用神；忌被冲克、空亡）',
            condition='月德天干五合（丙→辛，壬→丁，甲→己，庚→乙）',
            explanation='吉。《神煞赋》："月德合，灾不侵。"辅助月德增福，主平安顺遂。',
            source='《神煞赋》'
        )

        # 禄神
        self._add_shensha(
            name='禄神',
            category='吉神',
            definition='日主临官位（禄位），主俸禄、福寿、根基稳固',
            preference='喜见（禄神为用神、不被冲克；忌禄神被空亡、刑冲、忌神占）',
            condition='甲禄在寅、乙禄在卯、丙戊禄在巳、丁己禄在午、庚禄在申、辛禄在酉、壬禄在亥、癸禄在子',
            explanation='大吉。《渊海子平·论禄神》："禄者，爵禄也……主衣食丰足、福寿双全。"例：甲日主见寅木为禄神。',
            source='《渊海子平·论禄神》'
        )

        # 天厨贵人
        self._add_shensha(
            name='天厨贵人',
            category='吉神',
            definition='食禄之神，主饮食丰足、口福、文职贵气',
            preference='喜见（与食神同柱、生助财星；忌被枭神克制、空亡）',
            condition='甲见巳，乙见午，丙见子，丁见午，戊见申，己见酉，庚见亥，辛见子，壬见寅，癸见卯',
            explanation='吉。《神煞赋》："天厨贵人，食禄之官。"主烹饪、餐饮、文职顺利，享口福。',
            source='《神煞赋》'
        )

        # 红鸾
        self._add_shensha(
            name='红鸾',
            category='吉神',
            definition='婚恋喜庆之神，主动桃花、婚姻、添丁',
            preference='喜见（与日主相生、见合；忌被冲克、孤辰寡宿同现）',
            condition='年支查：申子辰见卯、亥卯未见子、寅午戌见酉、巳酉丑见午',
            explanation='吉（婚恋）。《渊海子平·论红鸾》："红鸾星动，婚姻必成。"主异性缘佳，宜婚嫁、添丁。',
            source='《渊海子平·论红鸾》'
        )

        # 天喜
        self._add_shensha(
            name='天喜',
            category='吉神',
            definition='红鸾对冲之神，主喜庆、添福、意外之喜',
            preference='喜见（与红鸾同现、生助用神；忌被凶煞冲克）',
            condition='年支查：申子辰见酉、亥卯未见午、寅午戌见卯、巳酉丑见子',
            explanation='吉。《神煞赋》："天喜照命，喜事临门。"主乔迁、升迁、中奖等意外喜庆。',
            source='《神煞赋》'
        )

        # 十灵日
        self._add_shensha(
            name='十灵日',
            category='吉神',
            definition='灵性聪慧之日，主悟性高、善思辨、易入宗教玄学',
            preference='喜见（与印星同柱、身强；忌被财星破印、身弱）',
            condition='甲辰、乙亥、丙辰、丁酉、戊午、庚戌、庚寅、辛亥、壬寅、癸未',
            explanation='吉（灵性）。《渊海子平·论十灵》："十灵日者，聪明智慧……主善文墨、通玄学。"',
            source='《渊海子平·论十灵》'
        )

        # 六秀日
        self._add_shensha(
            name='六秀日',
            category='吉神',
            definition='文才秀气之日，主文学、艺术天赋、考试顺利',
            preference='喜见（与食伤同柱、生助财官；忌被官杀克制、空亡）',
            condition='丙午、丁未、戊子、戊午、己丑、己未',
            explanation='吉（文才）。《神煞赋》："六秀聚顶，文章盖世。"主科举、文艺、创作有成。',
            source='《神煞赋》'
        )

        # 拱禄神
        self._add_shensha(
            name='拱禄神',
            category='吉神',
            definition='虚拱日主禄位（日时配合），主虚贵之气、晚年福寿',
            preference='喜见（拱禄位不被冲克、身强；忌拱位被刑冲、身弱）',
            condition='古诀：拱禄有五日五时：癸亥日癸丑时，癸丑日癸亥时，拱子禄；丁巳日丁未时，己未日己巳时，拱午禄；戊辰日戊午时，拱巳禄。查法以日柱配合时柱',
            explanation='吉（虚贵）。《渊海子平·论拱禄》："拱禄者，虚拱贵气……主晚年福寿，忌冲克。"',
            source='《渊海子平·论拱禄》'
        )

        # 血刃
        self._add_shensha(
            name='血刃',
            category='凶煞',
            definition='血光之灾煞，主外伤、手术、血光意外',
            preference='忌见（与羊刃同柱、身强；喜被官杀制、印星化）',
            condition='以月支查四柱地支：寅月丑、卯月未、辰月寅、巳月申、午月卯、未月酉、申月辰、酉月戌、戌月巳、亥月亥、子月午、丑月子',
            explanation='凶。《神煞赋》："血刃加临，血光难避。"主刀伤、流产、手术，需防意外。',
            source='《神煞赋》'
        )

        # 流霞
        self._add_shensha(
            name='流霞',
            category='凶煞',
            definition='血煞之液，主酒色、血光、意外灾祸',
            preference='忌见（日时柱见之、身弱；喜被食神制、印星化）',
            condition='日柱或时柱见：甲鸡（酉）、乙犬（戌）、丙羊（未）、丁猴（申）、戊蛇（巳）、己马（午）、庚龙（辰）、辛兔（卯）、壬猪（亥）、癸虎（寅）',
            explanation='凶。《渊海子平·论流霞》："男主酒色，女主产厄。"主饮酒误事、血光、婚姻不顺。',
            source='《渊海子平·论流霞》'
        )

        # 四废日
        self._add_shensha(
            name='四废日',
            category='凶煞',
            definition='五行衰绝之日，主诸事不顺、劳而无功',
            preference='忌见（日柱为四废、身弱；喜被印星生、身强）',
            condition='春（寅卯月）：庚申、辛酉（金废）；夏（巳午月）：壬子、癸亥（水废）；秋（申酉月）：甲寅、乙卯（木废）；冬（亥子月）：丙午、丁巳（火废）',
            explanation='凶。《神煞赋》："四废日主，做事难成。"主事业阻滞、投资失败，需待时运转。',
            source='《神煞赋》'
        )

        # 红艳煞
        self._add_shensha(
            name='红艳煞',
            category='凶煞',
            definition='风流桃花煞，主多情、外遇、感情纠纷',
            preference='忌见（日柱见之、身强；喜被官杀制、印星化）',
            condition='甲日午，乙日午，丙日寅，丁日未，戊日辰，己日辰，庚日戌，辛日酉，壬日子，癸日申（以日干查四柱地支）',
            explanation='凶（感情）。《渊海子平·论红艳》："红艳煞者，风流之宿……主多情纵欲，女主失节。"',
            source='《渊海子平·论红艳》'
        )

        # 飞刃
        self._add_shensha(
            name='飞刃',
            category='凶煞',
            definition='羊刃之对冲，主血光、刀刃之灾',
            preference='忌见（尤忌与羊刃同见）',
            condition='甲羊刃在卯，地支见酉即为飞刃；乙刃在寅，地支见申即为飞刃；丙戊羊刃在午，地支见子即为飞刃；丁己羊刃在巳，地支见亥即为飞刃；庚羊刃在酉，地支见卯即为飞刃；辛羊刃在申，地支见寅即为飞刃；壬羊刃在子，地支见午即为飞刃；癸羊刃在亥，地支见巳即为飞刃',
            explanation='凶。飞刃者，羊刃之对冲……主血光、刀刃之灾，比羊刃更凶。',
            source='《渊海子平·论飞刃》'
        )

        # 金神
        self._add_shensha(
            name='金神',
            category='凶煞',
            definition='刚烈凶煞，主争斗、血光、意外灾祸（需结合月令）',
            preference='忌见（生于火旺月、身弱；喜生于水旺月、身强、火制）',
            condition='日柱为乙丑、己巳、癸酉',
            explanation='凶（需制）。《渊海子平·论金神》："金神入火乡，富贵天下响……生于火月则凶，水月则吉。"主刚直易折，需火炼或水化。',
            source='《渊海子平·论金神》'
        )

        # 天转
        self._add_shensha(
            name='天转',
            category='凶煞',
            definition='天时逆转之煞，主灾厄、疾病、运势突变',
            preference='忌见（日柱见之、身弱；喜被印星化、官杀制）',
            condition='春（寅卯月）乙卯日、夏（巳午月）丙午日、秋（申酉月）辛酉日、冬（亥子月）壬子日',
            explanation='凶。《神煞赋》："天转地转，灾祸立见。"主突发灾病，需防意外。',
            source='《神煞赋》'
        )

        # 地转
        self._add_shensha(
            name='地转',
            category='凶煞',
            definition='地利逆转之煞，主迁移、动荡、家宅不宁',
            preference='忌见（日柱见之、身弱；喜被财星引化、印星稳）',
            condition='春（寅卯月）辛卯日、夏（巳午月）戊午日、秋（申酉月）癸酉日、冬（亥子月）丙子日',
            explanation='凶。《渊海子平·论地转》："地转者，迁移之神……主家宅变动、远行不利。"',
            source='《渊海子平·论地转》'
        )

        # 童子煞
        self._add_shensha(
            name='童子煞',
            category='凶煞',
            definition='童子命煞，主婚姻不顺、体弱多病、与宗教有缘',
            preference='忌见（日时柱见之、身弱；喜被送替身、修行化解）',
            condition='口诀："春秋寅子贵，冬夏卯未辰；金木马卯合，水火鸡犬多；土命逢辰巳，童子定不错。"（按生辰季节、日柱纳音查）',
            explanation='凶（婚姻）。《神煞赋》："童子煞者，前身仙童……主婚姻难成、多病灾。"需"还替身"或修行化解。',
            source='《神煞赋》'
        )

        # 八专
        self._add_shensha(
            name='八专',
            category='凶煞',
            definition='淫欲之煞，主情感混乱、夫妻不和、沉溺酒色',
            preference='忌见（日柱见之、身强；喜被官杀制、印星化）',
            condition='甲寅、乙卯、丁未、戊戌、己未、庚申、辛酉、癸丑',
            explanation='凶（感情）。《渊海子平·论八专》："八专日主，淫欲之征……主夫妻反目、外遇频发。"',
            source='《渊海子平·论八专》'
        )

        # 九丑
        self._add_shensha(
            name='九丑',
            category='凶煞',
            definition='婚姻丑事煞，主夫妻不和、丑闻、分离',
            preference='忌见（日柱见之、身弱；喜被财星稳、印星护）',
            condition='丁酉、戊子、戊午、己卯、己酉、辛卯、辛酉、壬子、壬午日',
            explanation='凶（婚姻）。《神煞赋》："九丑坐命，家门不宁。"主婚姻纠纷、名誉受损，需忍让化解。',
            source='《神煞赋》'
        )
    
    def _add_shensha(self, name: str, category: str, definition: str, 
                     preference: str, condition: str, explanation: str, source: str):
        """添加神煞到数据库"""
        info = ShenShaInfo(name, category, definition, preference, condition, explanation, source)
        self._shensha_dict[name] = info
    
    def get_shensha_info(self, name: str) -> Optional[ShenShaInfo]:
        """
        获取指定神煞的详细信息
        
        参数:
            name: 神煞名称
            
        返回:
            神煞信息对象,如果不存在则返回None
        """
        return self._shensha_dict.get(name)
    
    def get_shensha_dict(self, name: str) -> Optional[Dict]:
        """
        获取指定神煞的字典格式信息
        与 bazi_geju_refactored_v5.py 中的字段命名保持一致
        """
        info = self._shensha_dict.get(name)
        if not info:
            return None
        
        # 映射字段名以与 bazi_geju_refactored_v5.py 保持一致
        return {
            '概念描述': info.definition,
            '优点': '',  # 原数据库无此字段，留空
            '缺点': '',  # 原数据库无此字段，留空
            '心理特质': '',  # 原数据库无此字段，留空
            '年柱影响': '',  # 原数据库无此字段，留空
            '月柱影响': '',  # 原数据库无此字段，留空
            '日柱影响': '',  # 原数据库无此字段，留空
            '时柱影响': '',  # 原数据库无此字段，留空
            '男命成长建议': info.preference,
            '女命成长建议': info.preference,
            '成长建议': info.preference,
            # 原始字段也保留
            'name': info.name,
            'category': info.category,
            'definition': info.definition,
            'preference': info.preference,
            'condition': info.condition,
            'explanation': info.explanation,
            'source': info.source
        }
    
    def get_all_shensha(self) -> Dict[str, ShenShaInfo]:
        """获取所有神煞信息"""
        return self._shensha_dict.copy()
    
    def get_auspicious_shensha(self) -> Dict[str, ShenShaInfo]:
        """获取所有吉神"""
        return {k: v for k, v in self._shensha_dict.items() if v.category == '吉神'}
    
    def get_inauspicious_shensha(self) -> Dict[str, ShenShaInfo]:
        """获取所有凶煞"""
        return {k: v for k, v in self._shensha_dict.items() if v.category == '凶煞'}


class ShenShaCalculator:
    """
    神煞计算器
    用于计算八字四柱中包含的神煞
    """
    
    def __init__(self, database: ShenShaDatabase = None):
        """
        初始化神煞计算器
        
        参数:
            database: 神煞数据库对象,如果为None则创建新的
        """
        self.db = database if database is not None else ShenShaDatabase()
    
    def calculate(self, bazi: Dict[str, str]) -> Dict[str, List[str]]:
        """
        计算八字四柱中的神煞
        
        参数:
            bazi: 八字字典,格式为 {'year_gan': '甲', 'year_zhi': '子', 
                                     'month_gan': '乙', 'month_zhi': '丑',
                                     'day_gan': '丙', 'day_zhi': '寅',
                                     'time_gan': '丁', 'time_zhi': '卯'}
            
        返回:
            字典格式: {
                '年柱': ['天乙贵人', '文昌贵人'],
                '月柱': ['月德贵人', '将星'],
                '日柱': ['魁罡', '华盖'],
                '时柱': ['驿马', '金舆']
            }
        """
        result = {
            '年柱': [],
            '月柱': [],
            '日柱': [],
            '时柱': []
        }
        
        # 提取天干地支
        year_gan = bazi.get('year_gan', '')
        year_zhi = bazi.get('year_zhi', '')
        month_gan = bazi.get('month_gan', '')
        month_zhi = bazi.get('month_zhi', '')
        day_gan = bazi.get('day_gan', '')
        day_zhi = bazi.get('day_zhi', '')
        time_gan = bazi.get('time_gan', '')
        time_zhi = bazi.get('time_zhi', '')
        
        # 计算各柱神煞
        result['年柱'].extend(self._calculate_pillar_shensha(
            year_gan, year_zhi, day_gan, day_zhi, month_zhi, 'year', month_gan, time_gan, year_zhi, year_gan, time_zhi))
        result['月柱'].extend(self._calculate_pillar_shensha(
            month_gan, month_zhi, day_gan, day_zhi, month_zhi, 'month', month_gan, time_gan, year_zhi, year_gan, time_zhi))
        result['日柱'].extend(self._calculate_pillar_shensha(
            day_gan, day_zhi, day_gan, day_zhi, month_zhi, 'day', month_gan, time_gan, year_zhi, year_gan, time_zhi))
        result['时柱'].extend(self._calculate_pillar_shensha(
            time_gan, time_zhi, day_gan, day_zhi, month_zhi, 'time', month_gan, time_gan, year_zhi, year_gan, time_zhi))
        
        # 去重(神煞可以重复出现,所以不强制去重,但每个柱内去重)
        for pillar in result:
            result[pillar] = list(dict.fromkeys(result[pillar]))  # 保持顺序去重
        
        return result

    def calculate_dayun_liunian(self, dayun_liunian_gan: str, dayun_liunian_zhi: str,
                                dayun_liunian_type: str, original_bazi: Dict[str, str], is_male: bool = True) -> List[str]:
        """
        计算大运/流年的神煞

        参数:
            dayun_liunian_gan: 大运/流年天干
            dayun_liunian_zhi: 大运/流年地支
            dayun_liunian_type: 大运/流年类型 ('dayun' 或 'liunian')
            original_bazi: 原局八字字典
            is_male: 是否为男性（True-男，False-女）

        返回:
            大运/流年神煞列表
        """
        # 提取原局八字信息
        year_gan = original_bazi.get('year_gan', '')
        year_zhi = original_bazi.get('year_zhi', '')
        month_gan = original_bazi.get('month_gan', '')
        month_zhi = original_bazi.get('month_zhi', '')
        day_gan = original_bazi.get('day_gan', '')
        day_zhi = original_bazi.get('day_zhi', '')
        time_gan = original_bazi.get('time_gan', '')
        time_zhi = original_bazi.get('time_zhi', '')

        shenshas = []

        # ============ 大运流年神煞判定 ============
        # 只有满足a-h类判定逻辑的神煞才支持大运流年判定

        # a类：先查年干、日干，再看四柱地支类 → 补充：年干日干符合 → 再看大运流年地支
        shenshas.extend(self._check_tianyi_guiREN_dayun_liunian(day_gan, dayun_liunian_zhi, year_gan))
        shenshas.extend(self._check_taiji_guiREN_dayun_liunian(day_gan, dayun_liunian_zhi, year_gan))
        shenshas.extend(self._check_wenchang_guiREN_dayun_liunian(day_gan, dayun_liunian_zhi, year_gan))
        shenshas.extend(self._check_jinyu_dayun_liunian(dayun_liunian_gan, dayun_liunian_zhi, year_gan, day_gan))
        shenshas.extend(self._check_fuxing_dayun_liunian(dayun_liunian_gan, dayun_liunian_zhi, year_gan, day_gan))
        shenshas.extend(self._check_guoyin_dayun_liunian(day_gan, dayun_liunian_zhi, year_gan))
        shenshas.extend(self._check_tianchu_dayun_liunian(day_gan, dayun_liunian_zhi, year_gan))

        # b类：以日干查四地支类 → 补充：日干符合 → 再看大运流年地支
        shenshas.extend(self._check_huagai_dayun_liunian(dayun_liunian_zhi, year_zhi, day_zhi))
        shenshas.extend(self._check_jiangxing_dayun_liunian(dayun_liunian_zhi, year_zhi, day_zhi))
        shenshas.extend(self._check_yima_dayun_liunian(dayun_liunian_zhi, year_zhi, day_zhi))
        shenshas.extend(self._check_wangshen_dayun_liunian(dayun_liunian_zhi, year_zhi, day_zhi))
        shenshas.extend(self._check_xianchi_dayun_liunian(dayun_liunian_zhi, year_zhi, day_zhi))
        shenshas.extend(self._check_xuetang_dayun_liunian(day_gan, dayun_liunian_zhi))
        shenshas.extend(self._check_ciguan_dayun_liunian(day_gan, dayun_liunian_zhi))
        shenshas.extend(self._check_lushen_dayun_liunian(day_gan, dayun_liunian_zhi))
        shenshas.extend(self._check_yangren_dayun_liunian(day_gan, dayun_liunian_zhi))
        shenshas.extend(self._check_hongyan_sha_dayun_liunian(day_gan, dayun_liunian_zhi))
        shenshas.extend(self._check_liuxia_dayun_liunian(day_gan, dayun_liunian_zhi))

        # c类：先看月支，再看四柱地支类 → 补充：月支符合 → 再看大运流年地支
        shenshas.extend(self._check_xueren_dayun_liunian(month_zhi, dayun_liunian_zhi))
        shenshas.extend(self._check_tianyi_dayun_liunian(month_zhi, dayun_liunian_zhi))

        # d类：年支查其余三柱地支类 → 补充：年支符合 → 再看大运流年地支
        shenshas.extend(self._check_hongluan_dayun_liunian(year_zhi, dayun_liunian_zhi))
        shenshas.extend(self._check_tianxi_dayun_liunian(year_zhi, dayun_liunian_zhi))
        shenshas.extend(self._check_pima_dayun_liunian(year_zhi, dayun_liunian_zhi))
        shenshas.extend(self._check_sangmen_dayun_liunian(year_zhi, dayun_liunian_zhi))
        shenshas.extend(self._check_diaoke_dayun_liunian(year_zhi, dayun_liunian_zhi))
        shenshas.extend(self._check_baihu_dayun_liunian(year_zhi, dayun_liunian_zhi))
        shenshas.extend(self._check_tiangou_dayun_liunian(year_zhi, dayun_liunian_zhi))

        # e类：先看月支，再看四柱天干类 → 补充：月支符合 → 再看大运流年天干
        shenshas.extend(self._check_dexiu_dayun_liunian(month_zhi, dayun_liunian_gan))
        shenshas.extend(self._check_tiande_he_dayun_liunian(month_zhi, dayun_liunian_gan, dayun_liunian_zhi))
        shenshas.extend(self._check_yuede_he_dayun_liunian(month_zhi, dayun_liunian_gan))

        # h类：先看月支，再看四柱干支类 → 补充：月支符合 → 再看大运流年干支
        shenshas.extend(self._check_tiande_guiREN_dayun_liunian(month_zhi, dayun_liunian_gan, dayun_liunian_zhi))
        shenshas.extend(self._check_yuede_guiREN_dayun_liunian(month_zhi, dayun_liunian_gan))

        # f类：先查年支、日支，再看其余三柱地支类 → 补充：年支日支符合 → 再看大运流年地支
        shenshas.extend(self._check_jiesha_dayun_liunian(dayun_liunian_zhi, year_zhi, day_zhi))
        shenshas.extend(self._check_zhaisha_dayun_liunian(dayun_liunian_zhi, year_zhi, day_zhi))
        shenshas.extend(self._check_kongwang_dayun_liunian(year_gan, year_zhi, dayun_liunian_zhi, day_gan, day_zhi))
        shenshas.extend(self._check_tianluo_diwang_dayun_liunian(year_zhi, day_zhi, dayun_liunian_zhi))
        shenshas.extend(self._check_guchengus_dayun_liunian(year_zhi, dayun_liunian_zhi))
        shenshas.extend(self._check_yuanchen_dayun_liunian(dayun_liunian_zhi, year_zhi, year_gan, is_male))

        # g类：勾绞煞 → 以年支查大运/流年地支
        shenshas.extend(self._check_goujiao_dayun_liunian(dayun_liunian_zhi, year_zhi))

        # 去重并保持顺序
        result = list(dict.fromkeys(shenshas))
        # 调试输出
        # print(f"[调试shensha] 大运/流年: {dayun_liunian_gan}{dayun_liunian_zhi}, 原局月支: {month_zhi}, 日干: {day_gan}, 神煞: {result}")
        return result

    def _calculate_pillar_shensha(self, gan: str, zhi: str, day_gan: str,
                                   day_zhi: str, month_zhi: str, pillar_type: str,
                                   month_gan: str = '', time_gan: str = '', year_zhi: str = '',
                                   year_gan: str = '', time_zhi: str = '') -> List[str]:
        """
        计算单柱的神煞

        参数:
            gan: 天干
            zhi: 地支
            day_gan: 日干
            day_zhi: 日支
            month_zhi: 月支
            pillar_type: 柱类型('year', 'month', 'day', 'time')
            month_gan: 月干
            time_gan: 时干
            year_zhi: 年支
            year_gan: 年干
            time_zhi: 时支

        返回:
            该柱包含的神煞列表
        """
        shenshas = []

        # 计算各类神煞 - 按照最新规则修正

        # ========== 神煞分类信息 ============
        # a类：天乙贵人、太极贵人、文昌贵人、金舆、福星贵人、国印贵人、天厨贵人
        # b类：华盖、将星、驿马、亡神、咸池（桃花）、学堂、词馆、禄神、羊刃、六秀
        # c类：血刃、天医、六厄、天罗地网
        # d类：红鸾、天喜、元辰、披麻、丧门、吊客、白虎、天狗
        # e类：德秀贵人、天德合、月德合
        # f类：华盖、将星、驿马、亡神、咸池、金舆、劫煞、灾煞、空亡、孤辰寡宿、六厄、元辰
        # g类：勾绞煞（需性别信息）
        # h类：天德贵人、月德贵人（先看月支，再看四柱干支）
        # 以上分类仅用于大运流年判定，原局判定保持不变
        shenshas.extend(self._check_tianyi_guiREN(day_gan, zhi, year_gan, year_zhi, month_zhi, day_zhi, zhi))
        shenshas.extend(self._check_taiji_guiREN(day_gan, zhi, year_gan))
        shenshas.extend(self._check_wenchang_guiREN(day_gan, zhi, year_gan, year_zhi, month_zhi, day_zhi, zhi))
        shenshas.extend(self._check_tiande_guiREN(month_zhi, gan, zhi))
        shenshas.extend(self._check_yuede_guiREN(month_zhi, gan))
        shenshas.extend(self._check_huagai(zhi, pillar_type, year_zhi, day_zhi))
        shenshas.extend(self._check_jiangxing(zhi, pillar_type, year_zhi, day_zhi))
        shenshas.extend(self._check_yima(zhi, pillar_type, year_zhi, day_zhi))
        shenshas.extend(self._check_jinyu(gan, zhi, year_gan, day_gan))
        shenshas.extend(self._check_fuxing(gan, zhi, year_gan, day_gan))
        shenshas.extend(self._check_guoyin(day_gan, zhi))
        shenshas.extend(self._check_xuetang(day_gan, zhi))
        shenshas.extend(self._check_ciguan(day_gan, zhi))
        shenshas.extend(self._check_dexiu(month_zhi, gan))
        shenshas.extend(self._check_tianyi(month_zhi, zhi))
        shenshas.extend(self._check_kuigang(gan, zhi, pillar_type))
        shenshas.extend(self._check_yangren(day_gan, zhi))
        shenshas.extend(self._check_feiren(day_gan, zhi))
        shenshas.extend(self._check_jiesha(zhi, pillar_type, year_zhi, day_zhi))
        shenshas.extend(self._check_zhaisha(zhi, pillar_type, year_zhi, day_zhi))
        shenshas.extend(self._check_tianluo_diwang(gan, zhi, year_zhi, day_zhi, pillar_type))
        shenshas.extend(self._check_xunwang(day_gan, day_zhi, zhi, year_gan, year_zhi))
        shenshas.extend(self._check_shie_dabai(gan, zhi, pillar_type))
        shenshas.extend(self._check_xianchi(zhi, pillar_type, year_zhi, day_zhi))
        shenshas.extend(self._check_guchengus(zhi, pillar_type, year_zhi))
        shenshas.extend(self._check_yuanchen(zhi, pillar_type, year_zhi))
        shenshas.extend(self._check_liue(zhi, pillar_type, year_zhi, day_zhi))
        shenshas.extend(self._check_goujiao(zhi, pillar_type))
        shenshas.extend(self._check_guluan(gan, zhi, pillar_type))
        shenshas.extend(self._check_yinyang_chacuo(gan, zhi, pillar_type))
        shenshas.extend(self._check_wangshen(zhi, pillar_type, year_zhi, day_zhi))
        shenshas.extend(self._check_liuhai(zhi, pillar_type))
        shenshas.extend(self._check_pima(year_zhi, zhi, pillar_type))
        shenshas.extend(self._check_sangmen(year_zhi, zhi, pillar_type))
        shenshas.extend(self._check_diaoke(year_zhi, zhi, pillar_type))
        shenshas.extend(self._check_baihu(zhi, pillar_type))
        shenshas.extend(self._check_tiangou(zhi, pillar_type))
        shenshas.extend(self._check_sanqi(day_gan, month_gan, time_gan, year_gan))
        shenshas.extend(self._check_goujiao(zhi, pillar_type, year_zhi))

        # ============ 新增神煞 ============
        shenshas.extend(self._check_tiande_guiREN_he(month_zhi, year_gan, month_gan, day_gan, time_gan, year_zhi, day_zhi, zhi, pillar_type))
        shenshas.extend(self._check_yuede_guiREN_he(month_zhi, gan))
        shenshas.extend(self._check_tianshe_day(day_gan, zhi, pillar_type))
        shenshas.extend(self._check_lushen(day_gan, zhi))
        shenshas.extend(self._check_tianchu_guiREN(day_gan, zhi, year_gan, year_zhi, month_zhi, day_zhi, zhi))
        shenshas.extend(self._check_hongluan(year_zhi, zhi))
        shenshas.extend(self._check_tianxi(year_zhi, zhi))
        shenshas.extend(self._check_shiling(gan, zhi, pillar_type))
        shenshas.extend(self._check_liuxiu(gan, zhi, pillar_type))
        shenshas.extend(self._check_gonglu(day_gan, day_zhi, pillar_type, time_gan, time_zhi))
        shenshas.extend(self._check_xueren(month_zhi, zhi))
        shenshas.extend(self._check_liuxia(gan, zhi, pillar_type))
        shenshas.extend(self._check_sifei(month_zhi, gan, zhi, pillar_type))
        shenshas.extend(self._check_hongyan_sha(gan, zhi, pillar_type, year_gan, day_gan, year_zhi, month_zhi, day_zhi, time_zhi))
        shenshas.extend(self._check_jinshen(gan, zhi, pillar_type))
        shenshas.extend(self._check_tianzhuan(month_zhi, gan, zhi, pillar_type))
        shenshas.extend(self._check_dizhuan(month_zhi, gan, zhi, pillar_type))
        shenshas.extend(self._check_tongzisha(year_gan, year_zhi, month_zhi, day_zhi, zhi, pillar_type))
        shenshas.extend(self._check_bazhuan(gan, zhi, pillar_type))
        shenshas.extend(self._check_jiuchou(gan, zhi, pillar_type))

        return shenshas
    
    # ============ 各类神煞判断函数 ============
    
    def _check_tianyi_guiREN(self, day_gan: str, zhi: str, year_gan: str = '',
                              year_zhi: str = '', month_zhi: str = '',
                              day_zhi: str = '', time_zhi: str = '') -> List[str]:
        """
        检查天乙贵人（重构版 - 按照用户要求的逻辑）

        规则: 甲戊庚牛羊（丑未），乙己鼠猴乡（子申），
              丙丁猪鸡位（亥酉），壬癸兔蛇藏（卯巳），
              六辛逢马虎（寅午）

        判断逻辑：
        1. 首先判定年干和日干是否有甲、戊、庚之一
        2. 然后判断四柱地支是否有丑、未之一
        3. 在地支有丑、未之一的四柱标注有天乙贵人
        """
        # 天乙贵人对应关系映射
        tianyi_map = {
            '甲': ['丑', '未'],
            '戊': ['丑', '未'],
            '庚': ['丑', '未'],
            '乙': ['子', '申'],
            '己': ['子', '申'],
            '丙': ['亥', '酉'],
            '丁': ['亥', '酉'],
            '壬': ['卯', '巳'],
            '癸': ['卯', '巳'],
            '辛': ['寅', '午']
        }

        # 第一步：判定年干和日干是否有对应的天干
        # 收集年干和日干
        check_gans = []
        if year_gan:
            check_gans.append(year_gan)
        if day_gan:
            check_gans.append(day_gan)

        # 检查年干和日干是否有对应的天干（在规则中）
        has_valid_gan = False
        for gan in check_gans:
            if gan in tianyi_map:
                has_valid_gan = True
                break

        # 如果年干和日干都没有对应的天干，则不可能是天乙贵人
        if not has_valid_gan:
            return []

        # 第二步：判断四柱地支是否有对应的地支
        # 收集所有四柱地支
        all_zhis = [year_zhi, month_zhi, day_zhi, time_zhi]

        # 检查当前柱的地支是否是任意一个有效天干对应的贵人地支
        for gan in check_gans:
            if gan in tianyi_map:
                贵人地支 = tianyi_map.get(gan, [])
                if zhi in 贵人地支:
                    # 第三步：在地支有对应贵人地支的四柱标注有天乙贵人
                    return ['天乙贵人']

        return []
    
    def _check_taiji_guiREN(self, day_gan: str, zhi: str, year_gan: str = '') -> List[str]:
        """
        检查太极贵人（重构版 - 按照用户要求的逻辑）

        规则: 甲乙生人子午中，丙丁鸡兔定亨通；
              戊己两干临四季，庚辛寅亥禄丰隆；
              壬癸巳申偏喜美，值此应当福气钟

        判断逻辑：
        1. 首先判定年干和日干是否有对应的天干
        2. 然后判断四柱地支是否有对应的贵人地支
        3. 在地支有对应贵人地支的四柱标注有太极贵人
        """
        taiji_map = {
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

        # 第一步：判定年干和日干是否有对应的天干
        check_gans = []
        if year_gan:
            check_gans.append(year_gan)
        if day_gan:
            check_gans.append(day_gan)

        # 检查年干和日干是否有对应的天干（在规则中）
        has_valid_gan = False
        for gan in check_gans:
            if gan in taiji_map:
                has_valid_gan = True
                break

        # 如果年干和日干都没有对应的天干，则不可能是太极贵人
        if not has_valid_gan:
            return []

        # 第二步：判断四柱地支是否有对应的贵人地支
        # 检查当前柱的地支是否是任意一个有效天干对应的贵人地支
        for gan in check_gans:
            if gan in taiji_map:
                贵人地支 = taiji_map.get(gan, [])
                if zhi in 贵人地支:
                    # 第三步：在地支有对应贵人地支的四柱标注有太极贵人
                    return ['太极贵人']

        return []
    
    def _check_wenchang_guiREN(self, day_gan: str, zhi: str, year_gan: str = '',
                               year_zhi: str = '', month_zhi: str = '',
                               day_zhi: str = '', time_zhi: str = '') -> List[str]:
        """
        检查文昌贵人（重构版 - 按照用户要求的逻辑）

        规则: 甲乙巳午报君知，丙戊申宫丁己鸡；
              庚猪辛鼠壬逢虎，癸人见卯入云梯

        判断逻辑：
        1. 首先判定年干和日干是否有对应的天干
        2. 然后判断四柱地支是否有对应的贵人地支
        3. 在地支有对应贵人地支的四柱标注有文昌贵人
        """
        # 文昌贵人映射
        wenchang_map = {
            '甲': ['巳', '午'],
            '乙': ['巳', '午'],
            '丙': ['申'],
            '戊': ['申'],
            '丁': ['酉'],
            '己': ['酉'],
            '庚': ['亥'],
            '辛': ['子'],
            '壬': ['寅'],
            '癸': ['卯']
        }

        # 第一步：判定年干和日干是否有对应的天干
        # 收集年干和日干
        check_gans = []
        if year_gan:
            check_gans.append(year_gan)
        if day_gan:
            check_gans.append(day_gan)

        # 检查年干和日干是否有对应的天干（在规则中）
        has_valid_gan = False
        for gan in check_gans:
            if gan in wenchang_map:
                has_valid_gan = True
                break

        # 如果年干和日干都没有对应的天干，则不可能是文昌贵人
        if not has_valid_gan:
            return []

        # 第二步：判断四柱地支是否有对应的地支
        # 收集所有四柱地支
        all_zhis = [year_zhi, month_zhi, day_zhi, time_zhi]

        # 检查当前柱的地支是否是任意一个有效天干对应的贵人地支
        for gan in check_gans:
            if gan in wenchang_map:
                贵人地支 = wenchang_map.get(gan, [])
                if zhi in 贵人地支:
                    # 第三步：在地支有对应贵人地支的四柱标注有文昌贵人
                    return ['文昌贵人']

        return []
    
    def _check_tiande_guiREN(self, month_zhi: str, gan: str, zhi: str) -> List[str]:
        """
        检查天德贵人
        规则: 正月丁，二月申，三月壬，四月辛，
              五月亥，六月甲，七月癸，八月寅，
              九月丙，十月乙，十一月巳，十二月庚
        
        其中：丁、壬、辛、甲、癸、丙、乙、庚是天干；
              申、亥、寅、巳是地支
        
        判定逻辑：先看月支，再看四柱干支（天干或地支匹配即可）
        """
        # 天德映射: {月支: (类型, 值)}
        # 类型: 'gan'表示天干, 'zhi'表示地支
        tiande_map = {
            '寅': ('gan', '丁'),   # 正月丁
            '卯': ('zhi', '申'),   # 二月申
            '辰': ('gan', '壬'),   # 三月壬
            '巳': ('gan', '辛'),   # 四月辛
            '午': ('zhi', '亥'),   # 五月亥
            '未': ('gan', '甲'),   # 六月甲
            '申': ('gan', '癸'),   # 七月癸
            '酉': ('zhi', '寅'),   # 八月寅
            '戌': ('gan', '丙'),   # 九月丙
            '亥': ('gan', '乙'),   # 十月乙
            '子': ('zhi', '巳'),   # 十一月巳
            '丑': ('gan', '庚')    # 十二月庚
        }
        
        if month_zhi not in tiande_map:
            return []
        
        type_, value = tiande_map[month_zhi]
        
        if type_ == 'gan':
            # 天德对应天干，检查当前柱天干
            return ['天德贵人'] if gan == value else []
        else:
            # 天德对应地支，检查当前柱地支
            return ['天德贵人'] if zhi == value else []
    
    def _check_yuede_guiREN(self, month_zhi: str, gan: str) -> List[str]:
        """
        检查月德贵人
        规则: 寅午戌月丙，亥卯未月甲，申子辰月壬，巳酉丑月庚
        """
        if month_zhi in ['寅', '午', '戌']:
            return ['月德贵人'] if gan == '丙' else []
        elif month_zhi in ['亥', '卯', '未']:
            return ['月德贵人'] if gan == '甲' else []
        elif month_zhi in ['申', '子', '辰']:
            return ['月德贵人'] if gan == '壬' else []
        elif month_zhi in ['巳', '酉', '丑']:
            return ['月德贵人'] if gan == '庚' else []
        return []
    
    def _check_huagai(self, zhi: str, pillar_type: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """
        检查华盖
        规则: 寅午戌年/日见戌，亥卯未年/日见未，申子辰年/日见辰，巳酉丑年/日见丑
        以年支或日支为主,查四柱其他地支
        """
        huagai_map = {
            '寅': '戌', '午': '戌', '戌': '戌',
            '亥': '未', '卯': '未', '未': '未',
            '申': '辰', '子': '辰', '辰': '辰',
            '巳': '丑', '酉': '丑', '丑': '丑'
        }

        # 年支查
        年支华盖 = huagai_map.get(year_zhi, '')
        if zhi == 年支华盖:
            return ['华盖']

        # 日支查(排除日柱自身)
        if pillar_type != 'day':
            日支华盖 = huagai_map.get(day_zhi, '')
            if zhi == 日支华盖:
                return ['华盖']

        return []
    
    def _check_jiangxing(self, zhi: str, pillar_type: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """
        检查将星
        规则: 寅午戌年/日见午，亥卯未年/日见卯，申子辰年/日见子，巳酉丑年/日见酉
        以年支或日支为主,查四柱其他地支
        """
        jiangxing_map = {
            '寅': '午', '午': '午', '戌': '午',
            '亥': '卯', '卯': '卯', '未': '卯',
            '申': '子', '子': '子', '辰': '子',
            '巳': '酉', '酉': '酉', '丑': '酉'
        }

        # 年支查
        年支将星 = jiangxing_map.get(year_zhi, '')
        if zhi == 年支将星:
            return ['将星']

        # 日支查(排除日柱自身)
        if pillar_type != 'day':
            日支将星 = jiangxing_map.get(day_zhi, '')
            if zhi == 日支将星:
                return ['将星']

        return []
    
    def _check_yima(self, zhi: str, pillar_type: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """
        检查驿马
        规则: 申子辰年/日驿马在寅，寅午戌年/日驿马在申，
              亥卯未年/日驿马在巳，巳酉丑年/日驿马在亥
        以年支或日支为主,查四柱其他地支
        """
        yima_map = {
            '申': '寅', '子': '寅', '辰': '寅',
            '寅': '申', '午': '申', '戌': '申',
            '亥': '巳', '卯': '巳', '未': '巳',
            '巳': '亥', '酉': '亥', '丑': '亥'
        }

        # 年支查
        年支驿马 = yima_map.get(year_zhi, '')
        if zhi == 年支驿马:
            return ['驿马']

        # 日支查(排除日柱自身)
        if pillar_type != 'day':
            日支驿马 = yima_map.get(day_zhi, '')
            if zhi == 日支驿马:
                return ['驿马']

        return []
    
    def _check_jinyu(self, gan: str, zhi: str, year_gan: str = '', day_gan: str = '') -> List[str]:
        """
        检查金舆（重构版 - 按照用户要求的逻辑）

        规则: 甲龙乙蛇丙戊羊，丁己猴歌庚犬方；
              辛猪壬牛癸逢虎，此是金舆禄荣昌

        判断逻辑：
        1. 首先判定年干和日干是否有对应的天干
        2. 然后判断四柱地支是否有对应的金舆地支
        3. 在地支有对应金舆地支的四柱标注有金舆

        注意: 原规则是根据日干判断，现改为按照年干、日干查四柱地支的方式
        """
        # 金舆映射: {天干: [金舆地支]}
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

        # 第一步：判定年干和日干是否有对应的天干
        # 收集年干和日干
        check_gans = []
        if year_gan:
            check_gans.append(year_gan)
        if day_gan:
            check_gans.append(day_gan)

        # 检查年干和日干是否有对应的天干（在规则中）
        has_valid_gan = False
        for check_gan in check_gans:
            if check_gan in jinyu_map:
                has_valid_gan = True
                break

        # 如果年干和日干都没有对应的天干，则不可能是金舆
        if not has_valid_gan:
            return []

        # 第二步：判断四柱地支是否有对应的地支
        # 检查当前柱的地支是否是任意一个有效天干对应的金舆地支
        for check_gan in check_gans:
            if check_gan in jinyu_map:
                金舆地支列表 = jinyu_map.get(check_gan, [])
                if zhi in 金舆地支列表:
                    # 第三步：在地支有对应金舆地支的四柱标注有金舆
                    return ['金舆']

        return []
    

    
    def _check_fuxing(self, gan: str, zhi: str, year_gan: str = '', day_gan: str = '') -> List[str]:
        """
        检查福星贵人（重构版 - 按照用户要求的逻辑）

        规则: 甲丙相邀入虎乡（寅），更游鼠穴最高强（子）；
              戊猴己未丁宜亥（亥），乙癸逢牛卯禄昌（丑卯）；
              庚赶马头辛到巳（午巳），壬骑龙背喜非常（辰）

        具体规则:
        - 甲干：见寅或子
        - 丙干：见寅或子
        - 乙干：见卯或丑
        - 癸干：见卯或丑
        - 戊干：见申
        - 己干：见未
        - 丁干：见亥
        - 庚干：见午
        - 辛干：见巳
        - 壬干：见辰

        判断逻辑：
        1. 首先判定年干和日干是否有对应的天干
        2. 然后判断四柱地支是否有对应的福星贵人地支
        3. 在地支有对应福星贵人地支的四柱标注有福星贵人

        注意: 原规则是根据当前柱天干判断，现改为按照年干、日干查四柱地支的方式
        """
        # 福星贵人映射: {天干: [福星贵人地支]}
        fuxing_map = {
            '甲': ['寅', '子'],
            '丙': ['寅', '子'],
            '乙': ['卯', '丑'],
            '癸': ['卯', '丑'],
            '戊': ['申'],
            '己': ['未'],
            '丁': ['亥'],
            '庚': ['午'],
            '辛': ['巳'],
            '壬': ['辰']
        }

        # 第一步：判定年干和日干是否有对应的天干
        # 收集年干和日干
        check_gans = []
        if year_gan:
            check_gans.append(year_gan)
        if day_gan:
            check_gans.append(day_gan)

        # 检查年干和日干是否有对应的天干（在规则中）
        has_valid_gan = False
        for check_gan in check_gans:
            if check_gan in fuxing_map:
                has_valid_gan = True
                break

        # 如果年干和日干都没有对应的天干，则不可能是福星贵人
        if not has_valid_gan:
            return []

        # 第二步：判断四柱地支是否有对应的地支
        # 检查当前柱的地支是否是任意一个有效天干对应的福星贵人地支
        for check_gan in check_gans:
            if check_gan in fuxing_map:
                福星地支列表 = fuxing_map.get(check_gan, [])
                if zhi in 福星地支列表:
                    # 第三步：在地支有对应福星贵人地支的四柱标注有福星贵人
                    return ['福星贵人']

        return []
    
    def _check_guoyin(self, day_gan: str, zhi: str) -> List[str]:
        """
        检查国印贵人
        规则: 甲见戌，乙见亥，丙见丑，丁见寅，
              戊见丑，己见寅，庚见辰，辛见巳，
              壬见未，癸见申
        """
        guoyin_map = {
            '甲': '戌',
            '乙': '亥',
            '丙': '丑',
            '丁': '寅',
            '戊': '丑',
            '己': '寅',
            '庚': '辰',
            '辛': '巳',
            '壬': '未',
            '癸': '申'
        }
        
        国印地支 = guoyin_map.get(day_gan, '')
        return ['国印贵人'] if zhi == 国印地支 else []
    
    def _check_xuetang(self, day_gan: str, zhi: str) -> List[str]:
        """
        检查学堂
        规则: 甲见己亥，乙见壬午，丙见丙寅，丁见丁酉，
              戊见戊寅，己见己酉，庚见辛巳，辛见甲子，
              壬见甲申，癸见乙卯
        注意: 这里的地支是学堂地支
        """
        xuetang_map = {
            '甲': '亥',
            '乙': '午',
            '丙': '寅',
            '丁': '酉',
            '戊': '寅',
            '己': '酉',
            '庚': '巳',
            '辛': '子',
            '壬': '申',
            '癸': '卯'
        }
        
        学堂地支 = xuetang_map.get(day_gan, '')
        return ['学堂'] if zhi == 学堂地支 else []
    
    def _check_ciguan(self, day_gan: str, zhi: str) -> List[str]:
        """
        检查词馆
        规则: 甲见庚寅，乙见辛卯，丙见乙巳，丁见戊午，
              戊见丁巳，己见庚午，庚见壬申，辛见癸酉，
              壬见癸亥，癸见壬戌
        注意: 这里的地支是词馆地支
        """
        ciguan_map = {
            '甲': '寅',
            '乙': '卯',
            '丙': '巳',
            '丁': '午',
            '戊': '巳',
            '己': '午',
            '庚': '申',
            '辛': '酉',
            '壬': '亥',
            '癸': '戌'
        }
        
        词馆地支 = ciguan_map.get(day_gan, '')
        return ['词馆'] if zhi == 词馆地支 else []
    
    def _check_dexiu(self, month_zhi: str, gan: str) -> List[str]:
        """
        检查德秀贵人（修正版）

        规则:
        - 寅午戌月：丙丁为德，戊癸为秀
        - 申子辰月：壬癸戊己为德，丙辛甲己为秀
        - 巳酉丑月：庚辛为德，乙庚为秀
        - 亥卯未月：甲乙为德，丁壬为秀

        注意: 德秀贵人包含"德"和"秀"两部分，只要满足任一条件即可
        """
        if month_zhi in ['寅', '午', '戌']:
            # 寅午戌月：丙丁为德，戊癸为秀
            return ['德秀贵人'] if gan in ['丙', '丁', '戊', '癸'] else []
        elif month_zhi in ['申', '子', '辰']:
            # 申子辰月：壬癸戊己为德，丙辛甲己为秀
            return ['德秀贵人'] if gan in ['壬', '癸', '戊', '己', '丙', '辛', '甲'] else []
        elif month_zhi in ['巳', '酉', '丑']:
            # 巳酉丑月：庚辛为德，乙庚为秀
            return ['德秀贵人'] if gan in ['庚', '辛', '乙'] else []
        elif month_zhi in ['亥', '卯', '未']:
            # 亥卯未月：甲乙为德，丁壬为秀
            return ['德秀贵人'] if gan in ['甲', '乙', '丁', '壬'] else []
        return []
    
    def _check_tianyi(self, month_zhi: str, zhi: str) -> List[str]:
        """
        检查天医
        规则: 正月生见丑，二月生见寅，三月生见卯，四月生见辰，
              五月生见巳，六月生见午，七月生见未，八月生见申，
              九月生见酉，十月生见戌，十一月生见亥，十二月生见子
        """
        month_index = self.db.MONTH_ZHI.index(month_zhi) if month_zhi in self.db.MONTH_ZHI else 0
        tianyi_map = {
            0: '丑',  # 正月(寅)
            1: '寅',  # 二月(卯)
            2: '卯',  # 三月(辰)
            3: '辰',  # 四月(巳)
            4: '巳',  # 五月(午)
            5: '午',  # 六月(未)
            6: '未',  # 七月(申)
            7: '申',  # 八月(酉)
            8: '酉',  # 九月(戌)
            9: '戌',  # 十月(亥)
            10: '亥', # 十一月(子)
            11: '子'  # 十二月(丑)
        }
        
        天医地支 = tianyi_map.get(month_index, '')
        return ['天医'] if zhi == 天医地支 else []
    
    def _check_kuigang(self, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查魁罡
        规则: 日柱为壬辰、庚辰、戊戌、庚戌
        """
        if pillar_type == 'day':
            if (gan, zhi) in [('壬', '辰'), ('庚', '辰'), ('戊', '戌'), ('庚', '戌')]:
                return ['魁罡']
        return []
    
    def _check_yangren(self, day_gan: str, zhi: str) -> List[str]:
        """
        检查羊刃
        规则: 甲日卯，乙日寅，丙日午，丁日巳，戊日午，己日巳，庚日酉，辛日申，壬日子，癸日亥
        查法: 以日干查四地支
        """
        yangren_map = {
            '甲': '卯',
            '乙': '寅',
            '丙': '午',
            '丁': '巳',
            '戊': '午',
            '己': '巳',
            '庚': '酉',
            '辛': '申',
            '壬': '子',
            '癸': '亥'
        }

        羊刃地支 = yangren_map.get(day_gan, '')
        return ['羊刃'] if zhi == 羊刃地支 else []

    def _check_feiren(self, day_gan: str, zhi: str) -> List[str]:
        """
        检查飞刃
        规则: 甲羊刃在卯，地支见酉即为飞刃；乙刃在寅，地支见申即为飞刃；
              丙戊羊刃在午，地支见子即为飞刃；丁己羊刃在巳，地支见亥即为飞刃；
              庚羊刃在酉，地支见卯即为飞刃；辛羊刃在申，地支见寅即为飞刃；
              壬羊刃在子，地支见午即为飞刃；癸羊刃在亥，地支见巳即为飞刃
        查法: 以日干查四地支
        """
        # 飞刃是羊刃的对冲
        feiren_map = {
            '甲': '酉',  # 甲刃在卯，冲为酉
            '乙': '申',  # 乙刃在寅，冲为申
            '丙': '子',  # 丙刃在午，冲为子
            '丁': '亥',  # 丁刃在巳，冲为亥
            '戊': '子',  # 戊刃在午，冲为子
            '己': '亥',  # 己刃在巳，冲为亥
            '庚': '卯',  # 庚刃在酉，冲为卯
            '辛': '寅',  # 辛刃在申，冲为寅
            '壬': '午',  # 壬刃在子，冲为午
            '癸': '巳'   # 癸刃在亥，冲为巳
        }

        飞刃地支 = feiren_map.get(day_gan, '')
        return ['飞刃'] if zhi == 飞刃地支 else []

    def _check_jiesha(self, zhi: str, pillar_type: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """
        检查劫煞
        规则: 申子辰年/日见巳，亥卯未年/日见申，寅午戌年/日见亥，巳酉丑年/日见寅
        以年支或日支为主,查四柱其他地支
        """
        jiesha_map = {
            '申': '巳', '子': '巳', '辰': '巳',
            '亥': '申', '卯': '申', '未': '申',
            '寅': '亥', '午': '亥', '戌': '亥',
            '巳': '寅', '酉': '寅', '丑': '寅'
        }

        # 年支查
        年支劫煞 = jiesha_map.get(year_zhi, '')
        if zhi == 年支劫煞:
            return ['劫煞']

        # 日支查(排除日柱自身)
        if pillar_type != 'day':
            日支劫煞 = jiesha_map.get(day_zhi, '')
            if zhi == 日支劫煞:
                return ['劫煞']

        return []
    
    def _check_zhaisha(self, zhi: str, pillar_type: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """
        检查灾煞
        规则: 申子辰年/日劫煞在巳→灾煞在午；
              寅午戌年/日劫煞在亥→灾煞在子；
              亥卯未年/日劫煞在申→灾煞在酉；
              巳酉丑年/日劫煞在寅→灾煞在卯
        以年支或日支为主,查四柱其他地支
        """
        zhaisha_map = {
            '申': '午', '子': '午', '辰': '午',
            '寅': '子', '午': '子', '戌': '子',
            '亥': '酉', '卯': '酉', '未': '酉',
            '巳': '卯', '酉': '卯', '丑': '卯'
        }

        # 年支查
        年支灾煞 = zhaisha_map.get(year_zhi, '')
        if zhi == 年支灾煞:
            return ['灾煞']

        # 日支查(排除日柱自身)
        if pillar_type != 'day':
            日支灾煞 = zhaisha_map.get(day_zhi, '')
            if zhi == 日支灾煞:
                return ['灾煞']

        return []
    
    def _check_tianluo_diwang(self, gan: str, zhi: str, year_zhi: str = '', day_zhi: str = '', pillar_type: str = 'year') -> List[str]:
        """
        检查天罗地网
        规则: 先查【年支、日支】，再看【其余三柱地支】
              戌见亥、亥见戌为天罗
              辰见巳、巳见辰为地网
        """
        result = []

        # 如果当前柱是年柱或日柱，则不需要判定
        if pillar_type in ['year', 'day']:
            return []

        # 天罗：戌见亥、亥见戌
        # 检查年支
        if year_zhi in ['戌', '亥']:
            if zhi in ['戌', '亥'] and zhi != year_zhi:
                result.append('天罗地网')
        # 检查日支
        if day_zhi in ['戌', '亥']:
            if zhi in ['戌', '亥'] and zhi != day_zhi and pillar_type != 'year':
                result.append('天罗地网')

        # 地网：辰见巳、巳见辰
        # 检查年支
        if year_zhi in ['辰', '巳']:
            if zhi in ['辰', '巳'] and zhi != year_zhi:
                result.append('天罗地网')
        # 检查日支
        if day_zhi in ['辰', '巳']:
            if zhi in ['辰', '巳'] and zhi != day_zhi and pillar_type != 'year':
                result.append('天罗地网')

        return list(dict.fromkeys(result))
    
    def _check_xunwang(self, day_gan: str, day_zhi: str, zhi: str, year_gan: str = '',
                        year_zhi: str = '') -> List[str]:
        """
        检查空亡
        规则: 六十甲子每旬剩余两支为空亡
        优化逻辑：年柱、日柱都要查
        """
        # 定义各旬及其空亡地支
        xunkong_data = [
            # (旬名, 旬中的所有干支组合, 空亡地支)
            ('甲子旬', ['甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未', '壬申', '癸酉'], ('戌', '亥')),
            ('甲戌旬', ['甲戌', '乙亥', '丙子', '丁丑', '戊寅', '己卯', '庚辰', '辛巳', '壬午', '癸未'], ('申', '酉')),
            ('甲申旬', ['甲申', '乙酉', '丙戌', '丁亥', '戊子', '己丑', '庚寅', '辛卯', '壬辰', '癸巳'], ('午', '未')),
            ('甲午旬', ['甲午', '乙未', '丙申', '丁酉', '戊戌', '己亥', '庚子', '辛丑', '壬寅', '癸卯'], ('辰', '巳')),
            ('甲辰旬', ['甲辰', '乙巳', '丙午', '丁未', '戊申', '己酉', '庚戌', '辛亥', '壬子', '癸丑'], ('寅', '卯')),
            ('甲寅旬', ['甲寅', '乙卯', '丙辰', '丁巳', '戊午', '己未', '庚申', '辛酉', '壬戌', '癸亥'], ('子', '丑'))
        ]

        # 查年柱所在的旬
        year_xun_kongwang = None
        if year_gan and year_zhi:
            year_ganzhi = year_gan + year_zhi
            for xun_name, ganzhi_list, empty_zhis in xunkong_data:
                if year_ganzhi in ganzhi_list:
                    year_xun_kongwang = empty_zhis
                    break

        # 查日柱所在的旬
        day_xun_kongwang = None
        if day_gan and day_zhi:
            day_ganzhi = day_gan + day_zhi
            for xun_name, ganzhi_list, empty_zhis in xunkong_data:
                if day_ganzhi in ganzhi_list:
                    day_xun_kongwang = empty_zhis
                    break

        # 检查该地支是否在年柱或日柱的空亡地支中
        if year_xun_kongwang and zhi in year_xun_kongwang:
            return ['空亡']
        if day_xun_kongwang and zhi in day_xun_kongwang:
            return ['空亡']
        
        return []
    
    def _check_shie_dabai(self, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查十恶大败
        规则: 甲辰、乙巳、壬申、丙申、丁亥、庚辰、
              戊戌、癸亥、辛巳、己丑
        注意: 只适用于日柱
        """
        # 十恶大败只适用于日柱
        if pillar_type != 'day':
            return []

        bad_pillars = ['甲辰', '乙巳', '壬申', '丙申', '丁亥', 
                      '庚辰', '戊戌', '癸亥', '辛巳', '己丑']
        ganzhi = gan + zhi
        return ['十恶大败'] if ganzhi in bad_pillars else []
    
    def _check_xianchi(self, zhi: str, pillar_type: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """
        检查桃花（原咸池）
        规则: 寅午戌年/日见卯，亥卯未年/日见子，申子辰年/日见酉，巳酉丑年/日见午
        以年支或日支为主,查四柱其他地支
        """
        xianchi_map = {
            '寅': '卯', '午': '卯', '戌': '卯',
            '亥': '子', '卯': '子', '未': '子',
            '申': '酉', '子': '酉', '辰': '酉',
            '巳': '午', '酉': '午', '丑': '午'
        }

        # 年支查
        年支桃花 = xianchi_map.get(year_zhi, '')
        if zhi == 年支桃花:
            return ['桃花']

        # 日支查(排除日柱自身)
        if pillar_type != 'day':
            日支桃花 = xianchi_map.get(day_zhi, '')
            if zhi == 日支桃花:
                return ['桃花']

        return []
    
    def _check_guchengus(self, zhi: str, pillar_type: str, year_zhi: str = '') -> List[str]:
        """
        检查孤辰寡宿
        规则: 亥子丑年人，孤辰在寅，寡宿在戌；
              寅卯辰年人，孤辰在巳，寡宿在丑；
              巳午未年人，孤辰在申，寡宿在辰；
              申酉戌年人，孤辰在亥，寡宿在未
        以年支为主,查四柱其他地支
        """
        # 孤辰
        guchen_map = {
            '亥': '寅', '子': '寅', '丑': '寅',
            '寅': '巳', '卯': '巳', '辰': '巳',
            '巳': '申', '午': '申', '未': '申',
            '申': '亥', '酉': '亥', '戌': '亥'
        }
        # 寡宿
        gusu_map = {
            '亥': '戌', '子': '戌', '丑': '戌',
            '寅': '丑', '卯': '丑', '辰': '丑',
            '巳': '辰', '午': '辰', '未': '辰',
            '申': '未', '酉': '未', '戌': '未'
        }

        result = []
        年支孤辰 = guchen_map.get(year_zhi, '')
        年支寡宿 = gusu_map.get(year_zhi, '')

        if zhi == 年支孤辰:
            result.append('孤辰')
        if zhi == 年支寡宿:
            result.append('寡宿')

        return result
    
    def _check_yuanchen(self, zhi: str, pillar_type: str, year_zhi: str = '') -> List[str]:
        """
        检查元辰（大耗）
        规则: 阳男阴女：子年未，丑年申，寅年酉，卯年戌，辰年亥，巳年子，
              午年丑，未年寅，申年卯，酉年辰，戌年巳，亥年午
              阴男阳女：子年巳，丑年午，寅年未，卯年申，辰年酉，巳年戌，
              午年亥，未年子，申年丑，酉年寅，戌年卯，亥年辰
        查法: 以年支查余三支

        注意: 需要性别信息，这里简化处理，返回所有可能的元辰
        """
        # 元辰映射（阳男阴女）- 顺数前一位
        yuanchen_yang = {
            '子': '未', '丑': '申', '寅': '酉', '卯': '戌', '辰': '亥', '巳': '子',
            '午': '丑', '未': '寅', '申': '卯', '酉': '辰', '戌': '巳', '亥': '午'
        }

        # 元辰映射（阴男阳女）- 逆数前一位
        yuanchen_yin = {
            '子': '巳', '丑': '午', '寅': '未', '卯': '申', '辰': '酉', '巳': '戌',
            '午': '亥', '未': '子', '申': '丑', '酉': '寅', '戌': '卯', '亥': '辰'
        }

        result = []
        元辰_yang = yuanchen_yang.get(year_zhi, '')
        元辰_yin = yuanchen_yin.get(year_zhi, '')

        if zhi == 元辰_yang or zhi == 元辰_yin:
            result.append('元辰')

        return result
    
    def _check_liue(self, zhi: str, pillar_type: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """
        检查六厄
        规则: 申子辰年/日见卯，亥卯未年/日见午，寅午戌年/日见酉，巳酉丑年/日见子
        以年支或日支为主,查四柱其他地支
        """
        liue_map = {
            '申': '卯', '子': '卯', '辰': '卯',
            '亥': '午', '卯': '午', '未': '午',
            '寅': '酉', '午': '酉', '戌': '酉',
            '巳': '子', '酉': '子', '丑': '子'
        }

        # 年支查
        年支六厄 = liue_map.get(year_zhi, '')
        if zhi == 年支六厄:
            return ['六厄']

        # 日支查(排除日柱自身)
        if pillar_type != 'day':
            日支六厄 = liue_map.get(day_zhi, '')
            if zhi == 日支六厄:
                return ['六厄']

        return []
    
    def _check_goujiao(self, zhi: str, pillar_type: str, year_zhi: str = '') -> List[str]:
        """
        检查勾绞煞
        规则: 以年支查其余三柱地支
              子见卯，丑见辰，寅见巳，卯见午，辰见未，巳见申，
              午见酉，未见戌，申见亥，酉见子，戌见丑，亥见寅
        """
        # 勾绞煞映射: {年支: 对应地支}
        goujiao_map = {
            '子': '卯', '丑': '辰', '寅': '巳', '卯': '午',
            '辰': '未', '巳': '申', '午': '酉', '未': '戌',
            '申': '亥', '酉': '子', '戌': '丑', '亥': '寅'
        }

        # 排除年柱自身
        if pillar_type == 'year':
            return []

        勾绞位 = goujiao_map.get(year_zhi, '')
        return ['勾绞煞'] if zhi == 勾绞位 else []
    
    def _check_guluan(self, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查孤鸾煞
        规则: 乙巳、丁巳、辛亥、戊申、甲寅、丙午、戊午、壬子
        注意: 只适用于日柱
        """
        # 孤鸾煞只适用于日柱
        if pillar_type != 'day':
            return []

        guluan_pillars = ['乙巳', '丁巳', '辛亥', '戊申', '甲寅', '丙午', '戊午', '壬子']
        ganzhi = gan + zhi
        return ['孤鸾煞'] if ganzhi in guluan_pillars else []

    def _check_yinyang_chacuo(self, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查阴阳差错
        规则: 丙子、丁丑、戊寅、辛卯、壬辰、癸巳、
              丙午、丁未、戊申、辛酉、壬戌、癸亥
        注意: 只适用于日柱
        """
        # 阴阳差错只适用于日柱
        if pillar_type != 'day':
            return []

        chacuo_pillars = ['丙子', '丁丑', '戊寅', '辛卯', '壬辰', '癸巳',
                          '丙午', '丁未', '戊申', '辛酉', '壬戌', '癸亥']
        ganzhi = gan + zhi
        return ['阴阳差错'] if ganzhi in chacuo_pillars else []
    
    def _check_wangshen(self, zhi: str, pillar_type: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """
        检查亡神
        规则: 申子辰年/日见亥，亥卯未年/日见寅，寅午戌年/日见巳，巳酉丑年/日见申
        以年支或日支为主,查四柱其他地支
        """
        wangshen_map = {
            '申': '亥', '子': '亥', '辰': '亥',
            '亥': '寅', '卯': '寅', '未': '寅',
            '寅': '巳', '午': '巳', '戌': '巳',
            '巳': '申', '酉': '申', '丑': '申'
        }

        # 年支查
        年支亡神 = wangshen_map.get(year_zhi, '')
        if zhi == 年支亡神:
            return ['亡神']

        # 日支查(排除日柱自身)
        if pillar_type != 'day':
            日支亡神 = wangshen_map.get(day_zhi, '')
            if zhi == 日支亡神:
                return ['亡神']

        return []
    
    def _check_liuhai(self, zhi: str, pillar_type: str) -> List[str]:
        """
        检查六害（六穿）
        规则: 子未、丑午、寅巳、卯辰、申亥、酉戌
        需要与其他地支配合判断
        """
        # 六害需要两两相配,这里简化处理
        # 如果地支是其中之一,可能在六害关系中
        hai_pairs = ['子未', '丑午', '寅巳', '卯辰', '申亥', '酉戌']
        hai_zhis = ['子', '未', '丑', '午', '寅', '巳', '卯', '辰', '申', '亥', '酉', '戌']
        return []  # 需要完整八字判断,暂不实现
    
    def _check_pima(self, year_zhi: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查披麻
        规则: 以年支查余三支
              年支：子 丑 寅 卯 辰 巳 午 未 申 酉 戌 亥
              披麻：酉 戌 亥 子 丑 寅 卯 辰 巳 午 未 申
        """
        # 披麻映射: {年支: 对应地支}
        pima_map = {
            '子': '酉', '丑': '戌', '寅': '亥', '卯': '子',
            '辰': '丑', '巳': '寅', '午': '卯', '未': '辰',
            '申': '巳', '酉': '午', '戌': '未', '亥': '申'
        }

        披麻地支 = pima_map.get(year_zhi, '')
        return ['披麻'] if zhi == 披麻地支 else []

    def _check_sangmen(self, year_zhi: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查丧门
        规则: 以年支查余三支
              年支：子 丑 寅 卯 辰 巳 午 未 申 酉 戌 亥
              丧门：寅 卯 辰 巳 午 未 申 酉 戌 亥 子 丑
        """
        # 丧门映射: {年支: 对应地支}
        sangmen_map = {
            '子': '寅', '丑': '卯', '寅': '辰', '卯': '巳',
            '辰': '午', '巳': '未', '午': '申', '未': '酉',
            '申': '戌', '酉': '亥', '戌': '子', '亥': '丑'
        }

        丧门地支 = sangmen_map.get(year_zhi, '')
        return ['丧门'] if zhi == 丧门地支 else []

    def _check_diaoke(self, year_zhi: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查吊客
        规则: 以年支查余三支
              年支：子 丑 寅 卯 辰 巳 午 未 申 酉 戌 亥
              吊客：戌 亥 子 丑 寅 卯 辰 巳 午 未 申 酉
        """
        # 吊客映射: {年支: 对应地支}
        diaoke_map = {
            '子': '戌', '丑': '亥', '寅': '子', '卯': '丑',
            '辰': '寅', '巳': '卯', '午': '辰', '未': '巳',
            '申': '午', '酉': '未', '戌': '申', '亥': '酉'
        }

        吊客地支 = diaoke_map.get(year_zhi, '')
        return ['吊客'] if zhi == 吊客地支 else []
    
    def _check_baihu(self, zhi: str, pillar_type: str) -> List[str]:
        """
        检查白虎
        规则: 子年见午，丑年见未，寅年见申，卯年见酉，
              辰年见戌，巳年见亥，午年见子，未年见丑，
              申年见寅，酉年见卯，戌年见辰，亥年见巳
        注意: 需要年支信息
        """
        return []  # 需要年支信息,暂不实现
    
    def _check_tiangou(self, zhi: str, pillar_type: str) -> List[str]:
        """
        检查天狗
        规则: 子年见丑，丑年见寅，寅年见卯，卯年见辰，
              辰年见巳，巳年见午，午年见未，未年见申，
              申年见酉，酉年见戌，戌年见亥，亥年见子
        注意: 需要年支信息
        """
        return []  # 需要年支信息,暂不实现
    
    def _check_sanqi(self, day_gan: str, month_gan: str, time_gan: str, year_gan: str) -> List[str]:
        """
        检查三奇贵人
        规则: 乙丙丁、甲戊庚、壬癸辛三种组合
        需要满足以下四种顺排方式之一:
        1. 年月日顺排: 年干、月干、日干符合三奇
        2. 月日时顺排: 月干、日干、时干符合三奇
        3. 时日月顺排: 时干、日干、月干符合三奇
        4. 日月年顺排: 日干、月干、年干符合三奇
        """
        sanqi_sets = [
            ['乙', '丙', '丁'],
            ['甲', '戊', '庚'],
            ['壬', '癸', '辛']
        ]
        
        result = []
        
        # 检查四种顺排方式
        for sanqi_set in sanqi_sets:
            # 1. 年月日顺排
            if (year_gan == sanqi_set[0] and
                month_gan == sanqi_set[1] and
                day_gan == sanqi_set[2]):
                if '三奇贵人' not in result:
                    result.append('三奇贵人')
            
            # 2. 月日时顺排
            if (month_gan == sanqi_set[0] and
                day_gan == sanqi_set[1] and
                time_gan == sanqi_set[2]):
                if '三奇贵人' not in result:
                    result.append('三奇贵人')
            
            # 3. 时日月顺排
            if (time_gan == sanqi_set[0] and
                day_gan == sanqi_set[1] and
                month_gan == sanqi_set[2]):
                if '三奇贵人' not in result:
                    result.append('三奇贵人')
            
            # 4. 日月年顺排
            if (day_gan == sanqi_set[0] and
                month_gan == sanqi_set[1] and
                year_gan == sanqi_set[2]):
                if '三奇贵人' not in result:
                    result.append('三奇贵人')
        
        return result

    # ============ 新增神煞判断函数 ============

    def _check_tiande_guiREN_he(self, month_zhi: str, year_gan: str, month_gan: str,
                               day_gan: str, time_gan: str, year_zhi: str,
                               day_zhi: str, time_zhi: str, pillar_type: str) -> List[str]:
        """
        检查天德合
        规则: 先看月支，然后在年、日、时柱中查找对应的天干或地支

        口诀:
        寅月壬，卯月巳，辰月丁，巳月丙，午月寅，未月己，
        申月戊，酉月亥，戌月辛，亥月庚，子月申，丑月乙

        其中: 巳、寅、亥、申是地支，其他是天干

        示例:
        - 生于寅月，只要四柱天干中有壬，则该柱有天德合
        - 生于午月，只要四柱地支中有寅，则该柱有天德合
        """
        # 天德合映射: {月支: (类型, 值)}
        # 类型: 'gan'表示天干, 'zhi'表示地支
        tiandehe_map = {
            '寅': ('gan', '壬'),
            '卯': ('zhi', '巳'),
            '辰': ('gan', '丁'),
            '巳': ('gan', '丙'),
            '午': ('zhi', '寅'),
            '未': ('gan', '己'),
            '申': ('gan', '戊'),
            '酉': ('zhi', '亥'),
            '戌': ('gan', '辛'),
            '亥': ('gan', '庚'),
            '子': ('zhi', '申'),
            '丑': ('gan', '乙')
        }

        # 获取月支对应的天德合信息
        if month_zhi not in tiandehe_map:
            return []

        类型, 值 = tiandehe_map[month_zhi]

        # 根据柱类型返回对应的天德合状态
        if pillar_type == 'month':
            # 月柱本身不判断天德合
            return []
        elif pillar_type == 'year':
            if 类型 == 'gan':
                return ['天德合'] if year_gan == 值 else []
            else:
                return ['天德合'] if year_zhi == 值 else []
        elif pillar_type == 'day':
            if 类型 == 'gan':
                return ['天德合'] if day_gan == 值 else []
            else:
                return ['天德合'] if day_zhi == 值 else []
        elif pillar_type == 'time':
            if 类型 == 'gan':
                return ['天德合'] if time_gan == 值 else []
            else:
                return ['天德合'] if time_zhi == 值 else []

        return []

    def _check_yuede_guiREN_he(self, month_zhi: str, gan: str) -> List[str]:
        """
        检查月德合
        规则: 月德所在天干的正五合（丙→辛，壬→丁，甲→己，庚→乙）
        """
        if month_zhi in ['寅', '午', '戌']:
            月德天干 = '丙'
            月德合天干 = '辛'
        elif month_zhi in ['亥', '卯', '未']:
            月德天干 = '甲'
            月德合天干 = '己'
        elif month_zhi in ['申', '子', '辰']:
            月德天干 = '壬'
            月德合天干 = '丁'
        elif month_zhi in ['巳', '酉', '丑']:
            月德天干 = '庚'
            月德合天干 = '乙'
        else:
            return []

        return ['月德合'] if gan == 月德合天干 else []

    def _check_tianshe_day(self, day_gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查天赦日
        规则: 春季戊寅日、夏季甲午日、秋季戊申日、冬季甲子日
        注意: 只适用于日柱
        """
        # 天赦日只适用于日柱
        if pillar_type != 'day':
            return []

        tianshe_days = ['戊寅', '甲午', '戊申', '甲子']
        ganzhi = day_gan + zhi
        return ['天赦'] if ganzhi in tianshe_days else []

    def _check_lushen(self, day_gan: str, zhi: str) -> List[str]:
        """
        检查禄神
        规则: 甲禄在寅、乙禄在卯、丙戊禄在巳、丁己禄在午、庚禄在申、辛禄在酉、壬禄在亥、癸禄在子
        """
        lushen_map = {
            '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
            '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
            '壬': '亥', '癸': '子'
        }

        禄位 = lushen_map.get(day_gan, '')
        return ['禄神'] if zhi == 禄位 else []

    def _check_tianchu_guiREN(self, day_gan: str, zhi: str, year_gan: str = '',
                              year_zhi: str = '', month_zhi: str = '',
                              day_zhi: str = '', time_zhi: str = '') -> List[str]:
        """
        检查天厨贵人（重构版 - 按照用户要求的逻辑）

        规则: 甲干见巳，乙干见午，丙干见子，丁干见午，
              戊干见申，己干见酉，庚干见亥，辛干见子，
              壬干见寅，癸干见卯

        判断逻辑：
        1. 首先判定年干和日干是否有对应的天干
        2. 然后判断四柱地支是否有对应的贵人地支
        3. 在地支有对应贵人地支的四柱标注有天厨贵人
        """
        # 天厨贵人映射
        tianchu_map = {
            '甲': '巳',
            '乙': '午',
            '丙': '子',
            '丁': '午',
            '戊': '申',
            '己': '酉',
            '庚': '亥',
            '辛': '子',
            '壬': '寅',
            '癸': '卯'
        }

        # 第一步：判定年干和日干是否有对应的天干
        # 收集年干和日干
        check_gans = []
        if year_gan:
            check_gans.append(year_gan)
        if day_gan:
            check_gans.append(day_gan)

        # 检查年干和日干是否有对应的天干（在规则中）
        has_valid_gan = False
        for gan in check_gans:
            if gan in tianchu_map:
                has_valid_gan = True
                break

        # 如果年干和日干都没有对应的天干，则不可能是天厨贵人
        if not has_valid_gan:
            return []

        # 第二步：判断四柱地支是否有对应的地支
        # 收集所有四柱地支
        all_zhis = [year_zhi, month_zhi, day_zhi, time_zhi]

        # 检查当前柱的地支是否是任意一个有效天干对应的贵人地支
        for gan in check_gans:
            if gan in tianchu_map:
                贵人地支 = tianchu_map.get(gan, '')
                if zhi == 贵人地支:
                    # 第三步：在地支有对应贵人地支的四柱标注有天厨贵人
                    return ['天厨贵人']

        return []

    def _check_hongluan(self, year_zhi: str, zhi: str) -> List[str]:
        """
        检查红鸾
        规则: 以年支为基准，对应关系为：
              年支:子丑寅卯辰巳午未申酉戌亥
              三地支见:卯寅丑子亥戌酉申未午已辰
        """
        # 红鸾映射: {年支: 对应地支}
        hongluan_map = {
            '子': '卯', '丑': '寅', '寅': '丑', '卯': '子',
            '辰': '亥', '巳': '戌', '午': '酉', '未': '申',
            '申': '未', '酉': '午', '戌': '巳', '亥': '辰'
        }

        红鸾位 = hongluan_map.get(year_zhi, '')
        return ['红鸾'] if zhi == 红鸾位 else []

    def _check_tianxi(self, year_zhi: str, zhi: str) -> List[str]:
        """
        检查天喜
        规则: 以年支为基准，对应关系为：
              年支查其余地支：子见酉、丑见申、寅见未、卯见午、辰见巳、巳见辰、
                              午见卯、未见寅、申见丑、酉见子、戌见亥、亥见戌
        """
        # 天喜映射: {年支: 对应地支}
        tianxi_map = {
            '子': '酉', '丑': '申', '寅': '未', '卯': '午',
            '辰': '巳', '巳': '辰', '午': '卯', '未': '寅',
            '申': '丑', '酉': '子', '戌': '亥', '亥': '戌'
        }

        天喜位 = tianxi_map.get(year_zhi, '')
        return ['天喜'] if zhi == 天喜位 else []

    def _check_shiling(self, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查十灵日
        规则: 甲辰、乙亥、丙辰、丁酉、戊午、庚戌、庚寅、辛亥、壬寅、癸未
        注意: 只适用于日柱
        """
        # 十灵日只适用于日柱
        if pillar_type != 'day':
            return []

        shiling_days = ['甲辰', '乙亥', '丙辰', '丁酉', '戊午', '庚戌', '庚寅', '辛亥', '壬寅', '癸未']
        ganzhi = gan + zhi
        return ['十灵日'] if ganzhi in shiling_days else []

    def _check_liuxiu(self, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查六秀日
        规则: 丙午、丁未、戊子、戊午、己丑、己未
        注意: 只适用于日柱
        """
        # 六秀日只适用于日柱
        if pillar_type != 'day':
            return []

        liuxiu_days = ['丙午', '丁未', '戊子', '戊午', '己丑', '己未']
        ganzhi = gan + zhi
        return ['六秀日'] if ganzhi in liuxiu_days else []

    def _check_gonglu(self, day_gan: str, zhi: str, pillar_type: str, time_gan: str = '', time_zhi: str = '') -> List[str]:
        """
        检查拱禄神
        古诀：拱禄有五日五时：癸亥日癸丑时，癸丑日癸亥时，拱子禄；
              丁巳日丁未时，己未日己巳时，拱午禄；
              戊辰日戊午时，拱巳禄。
        查法: 以日柱配合时柱
        注意: 只适用于时柱（日时配合判定）
        """
        # 拱禄神在时柱判断，需要日时配合
        if pillar_type != 'time':
            return []

        day_ganzhi = day_gan + zhi  # 日柱干支
        time_ganzhi = time_gan + time_zhi  # 时柱干支

        # 拱禄组合：日柱+时柱
        gonglu_pairs = [
            # 拱子禄（癸日）
            ('癸亥', '癸丑'),  # 癸亥日癸丑时
            ('癸丑', '癸亥'),  # 癸丑日癸亥时
            # 拱午禄
            ('丁巳', '丁未'),  # 丁巳日丁未时，拱午禄
            ('己未', '己巳'),  # 己未日己巳时，拱午禄
            # 拱巳禄
            ('戊辰', '戊午'),  # 戊辰日戊午时，拱巳禄
        ]

        for day_pair, time_pair in gonglu_pairs:
            if day_ganzhi == day_pair and time_ganzhi == time_pair:
                return ['拱禄神']

        return []

    def _check_xueren(self, month_zhi: str, zhi: str) -> List[str]:
        """
        检查血刃（修正版）

        规则: 以月支查四柱地支
        - 寅月：丑
        - 卯月：未
        - 辰月：寅
        - 巳月：申
        - 午月：卯
        - 未月：酉
        - 申月：辰
        - 酉月：戌
        - 戌月：巳
        - 亥月：亥
        - 子月：午
        - 丑月：子

        注意: 按照月支查四柱地支，匹配即为血刃
        """
        # 血刃映射: {月支: 血刃地支}
        xueren_map = {
            '寅': '丑',
            '卯': '未',
            '辰': '寅',
            '巳': '申',
            '午': '卯',
            '未': '酉',
            '申': '辰',
            '酉': '戌',
            '戌': '巳',
            '亥': '亥',
            '子': '午',
            '丑': '子'
        }

        血刃地支 = xueren_map.get(month_zhi, '')
        return ['血刃'] if zhi == 血刃地支 else []

    def _check_liuxia(self, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查流霞
        规则: 甲鸡（酉）、乙犬（戌）、丙羊（未）、丁猴（申）、
              戊蛇（巳）、己马（午）、庚龙（辰）、辛兔（卯）、
              壬猪（亥）、癸虎（寅）
        注意: 只适用于日柱和时柱
        """
        # 流霞只适用于日柱和时柱
        if pillar_type not in ['day', 'time']:
            return []

        liuxia_map = {
            '甲': '酉', '乙': '戌', '丙': '未', '丁': '申',
            '戊': '巳', '己': '午', '庚': '辰', '辛': '卯',
            '壬': '亥', '癸': '寅'
        }

        流霞位 = liuxia_map.get(gan, '')
        return ['流霞'] if zhi == 流霞位 else []

    def _check_sifei(self, month_zhi: str, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查四废日
        规则: 春（寅卯月）：庚申、辛酉（金废）
              夏（巳午月）：壬子、癸亥（水废）
              秋（申酉月）：甲寅、乙卯（木废）
              冬（亥子月）：丙午、丁巳（火废）
        注意: 只适用于日柱
        """
        # 四废日只适用于日柱
        if pillar_type != 'day':
            return []

        ganzhi = gan + zhi

        # 春季
        if month_zhi in ['寅', '卯']:
            四废日 = ['庚申', '辛酉']
        # 夏季
        elif month_zhi in ['巳', '午']:
            四废日 = ['壬子', '癸亥']
        # 秋季
        elif month_zhi in ['申', '酉']:
            四废日 = ['甲寅', '乙卯']
        # 冬季
        elif month_zhi in ['亥', '子']:
            四废日 = ['丙午', '丁巳']
        else:
            return []

        return ['四废日'] if ganzhi in 四废日 else []

    def _check_hongyan_sha(self, gan: str, zhi: str, pillar_type: str,
                            year_gan: str = '', day_gan: str = '',
                            year_zhi: str = '', month_zhi: str = '',
                            day_zhi: str = '', time_zhi: str = '') -> List[str]:
        """
        检查红艳煞（优化版）

        判定逻辑：以【日干】查【四柱地支】
        检查当前柱地支是否匹配日干对应的地支

        规则映射：
        甲日→午，乙日→午，丙日→寅，丁日→未，戊日→辰，
        己日→辰，庚日→戌，辛日→酉，壬日→子，癸日→申
        """
        # 红艳煞映射: {日干: 红艳煞地支}
        hongyan_map = {
            '甲': '午',
            '乙': '午',
            '丙': '寅',
            '丁': '未',
            '戊': '辰',
            '己': '辰',
            '庚': '戌',
            '辛': '酉',
            '壬': '子',
            '癸': '申'
        }

        # 检查日干是否在规则映射中
        if day_gan not in hongyan_map:
            return []

        # 获取日干对应的红艳煞地支
        target_zhi = hongyan_map[day_gan]

        # 检查当前柱地支是否匹配
        if zhi == target_zhi:
            return ['红艳煞']

        return []

    def _check_jinshen(self, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查金神
        规则: 乙丑、己巳、癸酉
        注意: 只适用于日柱
        """
        # 金神只适用于日柱
        if pillar_type != 'day':
            return []

        jinshen_days = ['乙丑', '己巳', '癸酉']
        ganzhi = gan + zhi
        return ['金神'] if ganzhi in jinshen_days else []

    def _check_tianzhuan(self, month_zhi: str, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查天转
        古诀："春兔夏马天地转，秋鸡冬鼠便为殃;行人在路须忧死，造恶未成先架丧。"
        规则: 寅卯辰月见乙卯日，巳午未月见丙午日，申酉戌月见辛酉日，亥子丑月见壬子日
        查法: 以月支查日柱
        注意: 只适用于日柱
        """
        # 天转只适用于日柱
        if pillar_type != 'day':
            return []

        ganzhi = gan + zhi

        # 春季：寅、卯、辰月 - 见乙卯日
        if month_zhi in ['寅', '卯', '辰']:
            return ['天转'] if ganzhi == '乙卯' else []
        # 夏季：巳、午、未月 - 见丙午日
        elif month_zhi in ['巳', '午', '未']:
            return ['天转'] if ganzhi == '丙午' else []
        # 秋季：申、酉、戌月 - 见辛酉日
        elif month_zhi in ['申', '酉', '戌']:
            return ['天转'] if ganzhi == '辛酉' else []
        # 冬季：亥、子、丑月 - 见壬子日
        elif month_zhi in ['亥', '子', '丑']:
            return ['天转'] if ganzhi == '壬子' else []
        return []

    def _check_dizhuan(self, month_zhi: str, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查地转
        规则: 寅卯辰月见辛卯日，巳午未月见戊午日，申酉戌月癸酉日，亥子丑月见丙子日
        查法: 以月支查日柱
        注意: 只适用于日柱
        """
        # 地转只适用于日柱
        if pillar_type != 'day':
            return []

        ganzhi = gan + zhi

        # 春季：寅、卯、辰月 - 见辛卯日
        if month_zhi in ['寅', '卯', '辰']:
            return ['地转'] if ganzhi == '辛卯' else []
        # 夏季：巳、午、未月 - 见戊午日
        elif month_zhi in ['巳', '午', '未']:
            return ['地转'] if ganzhi == '戊午' else []
        # 秋季：申、酉、戌月 - 见癸酉日
        elif month_zhi in ['申', '酉', '戌']:
            return ['地转'] if ganzhi == '癸酉' else []
        # 冬季：亥、子、丑月 - 见丙子日
        elif month_zhi in ['亥', '子', '丑']:
            return ['地转'] if ganzhi == '丙子' else []
        return []

    def _check_tongzisha(self, year_gan: str, year_zhi: str, month_zhi: str,
                          day_zhi: str, time_zhi: str, pillar_type: str) -> List[str]:
        """
        检查童子煞
        规则:
        1. 命造生在春季或秋季的（以月令算），日支或时支见寅或子的
        2. 命造生在冬季或夏季的（以月令算），日支或时支见卯、未或辰的
        3. 年柱纳音为金或木的，日支或时支见午或卯的
        4. 年柱纳音为水或火的，日支或时支见酉或戌的
        5. 年柱纳音为土命的，日支或时支见辰或巳的

        注意: 只适用于日柱和时柱
        """
        # 童子煞只适用于日柱和时柱
        if pillar_type not in ['day', 'time']:
            return []

        # 获取年柱纳音
        year_nayin = self.db.NAYIN.get((year_gan, year_zhi), '')
        if not year_nayin:
            return []

        result = []

        # 判断季节（以月令为准）
        # 春季：寅、卯、辰月
        # 夏季：巳、午、未月
        # 秋季：申、酉、戌月
        # 冬季：亥、子、丑月
        if month_zhi in ['寅', '卯', '辰'] or month_zhi in ['申', '酉', '戌']:
            # 春季或秋季：日支或时支见寅或子
            if pillar_type == 'day':
                if day_zhi in ['寅', '子']:
                    result.append('童子煞')
            elif pillar_type == 'time':
                if time_zhi in ['寅', '子']:
                    result.append('童子煞')

        elif month_zhi in ['巳', '午', '未'] or month_zhi in ['亥', '子', '丑']:
            # 夏季或冬季：日支或时支见卯、未或辰
            if pillar_type == 'day':
                if day_zhi in ['卯', '未', '辰']:
                    result.append('童子煞')
            elif pillar_type == 'time':
                if time_zhi in ['卯', '未', '辰']:
                    result.append('童子煞')

        # 根据年柱纳音判断
        if '金' in year_nayin or '木' in year_nayin:
            # 年柱纳音为金或木：日支或时支见午或卯
            if pillar_type == 'day':
                if day_zhi in ['午', '卯'] and '童子煞' not in result:
                    result.append('童子煞')
            elif pillar_type == 'time':
                if time_zhi in ['午', '卯'] and '童子煞' not in result:
                    result.append('童子煞')

        elif '水' in year_nayin or '火' in year_nayin:
            # 年柱纳音为水或火：日支或时支见酉或戌
            if pillar_type == 'day':
                if day_zhi in ['酉', '戌'] and '童子煞' not in result:
                    result.append('童子煞')
            elif pillar_type == 'time':
                if time_zhi in ['酉', '戌'] and '童子煞' not in result:
                    result.append('童子煞')

        elif '土' in year_nayin:
            # 年柱纳音为土：日支或时支见辰或巳
            if pillar_type == 'day':
                if day_zhi in ['辰', '巳'] and '童子煞' not in result:
                    result.append('童子煞')
            elif pillar_type == 'time':
                if time_zhi in ['辰', '巳'] and '童子煞' not in result:
                    result.append('童子煞')

        return result

    def _check_bazhuan(self, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查八专
        规则: 甲寅、乙卯、丁未、戊戌、己未、庚申、辛酉、癸丑
              （干支同气，阴阳相同）
        注意: 只适用于日柱
        """
        # 八专只适用于日柱
        if pillar_type != 'day':
            return []

        bazhuan_days = ['甲寅', '乙卯', '丁未', '戊戌', '己未', '庚申', '辛酉', '癸丑']
        ganzhi = gan + zhi
        return ['八专'] if ganzhi in bazhuan_days else []

    def _check_jiuchou(self, gan: str, zhi: str, pillar_type: str) -> List[str]:
        """
        检查九丑
        古诀: 丁酉日、戊子日、戊午日、己卯日、己酉日、辛卯日、辛酉日、壬子日、壬午日
        查法: 查日柱
        注意: 只适用于日柱
        """
        # 九丑只适用于日柱
        if pillar_type != 'day':
            return []

        jiuchou_days = ['丁酉', '戊子', '戊午', '己卯', '己酉', '辛卯', '辛酉', '壬子', '壬午']
        ganzhi = gan + zhi
        return ['九丑'] if ganzhi in jiuchou_days else []

    # ============ 大运流年神煞判定方法 ============

    def _check_tianyi_guiREN_dayun_liunian(self, day_gan: str, liunian_zhi: str, year_gan: str = '') -> List[str]:
        """
        天乙贵人 - 大运流年版（a类）
        原规则：甲戊庚牛羊（丑未），乙己鼠猴乡（子申），
              丙丁猪鸡位（亥酉），壬癸兔蛇藏（卯巳），六辛逢马虎（寅午）
        补充规则：年干/日干符合 → 再看大运/流年地支
        """
        tianyi_map = {
            '甲': ['丑', '未'], '戊': ['丑', '未'], '庚': ['丑', '未'],
            '乙': ['子', '申'], '己': ['子', '申'],
            '丙': ['亥', '酉'], '丁': ['亥', '酉'],
            '壬': ['卯', '巳'], '癸': ['卯', '巳'],
            '辛': ['寅', '午']
        }
        # 检查年干和日干
        check_gans = [year_gan, day_gan]
        for gan in check_gans:
            if gan in tianyi_map and liunian_zhi in tianyi_map.get(gan, []):
                return ['天乙贵人']
        return []

    def _check_taiji_guiREN_dayun_liunian(self, day_gan: str, liunian_zhi: str, year_gan: str = '') -> List[str]:
        """
        太极贵人 - 大运流年版（a类）
        原规则：甲乙生人子午中，丙丁鸡兔定亨通；
              戊己两干临四季，庚辛寅亥禄丰隆；
              壬癸巳申偏喜美，值此应当福气钟
        补充规则：年干/日干符合 → 再看大运/流年地支
        """
        taiji_map = {
            '甲': ['子', '午'], '乙': ['子', '午'],
            '丙': ['酉', '卯'], '丁': ['酉', '卯'],
            '戊': ['辰', '戌', '丑', '未'], '己': ['辰', '戌', '丑', '未'],
            '庚': ['寅', '亥'], '辛': ['寅', '亥'],
            '壬': ['巳', '申'], '癸': ['巳', '申']
        }
        # 检查年干和日干
        check_gans = [year_gan, day_gan]
        for gan in check_gans:
            if gan in taiji_map and liunian_zhi in taiji_map.get(gan, []):
                return ['太极贵人']
        return []

    def _check_wenchang_guiREN_dayun_liunian(self, day_gan: str, liunian_zhi: str, year_gan: str = '') -> List[str]:
        """
        文昌贵人 - 大运流年版（a类）
        原规则：甲乙巳午报君知，丙戊申宫丁己鸡；
              庚猪辛鼠壬逢虎，癸人见卯入云梯
        补充规则：年干/日干符合 → 再看大运/流年地支
        """
        wenchang_map = {
            '甲': ['巳'], '乙': ['午'],
            '丙': ['申'], '戊': ['申'],
            '丁': ['酉'], '己': ['酉'],
            '庚': ['亥'], '辛': ['子'],
            '壬': ['寅'], '癸': ['卯']
        }
        # 检查年干和日干
        check_gans = [year_gan, day_gan]
        for gan in check_gans:
            if gan in wenchang_map and liunian_zhi in wenchang_map.get(gan, []):
                return ['文昌贵人']
        return []

    def _check_jinyu_dayun_liunian(self, liunian_gan: str, liunian_zhi: str, year_gan: str = '', day_gan: str = '') -> List[str]:
        """金舆 - 大运流年版（a类）"""
        jinyu_map = {
            '甲': ['辰'], '乙': ['巳'],
            '丙': ['未'], '戊': ['未'],
            '丁': ['申'], '己': ['申'],
            '庚': ['戌'], '辛': ['亥'],
            '壬': ['丑'], '癸': ['寅']
        }
        check_gans = [g for g in [year_gan, day_gan] if g]
        for gan in check_gans:
            if gan in jinyu_map and liunian_zhi in jinyu_map.get(gan, []):
                return ['金舆']
        return []

    def _check_fuxing_dayun_liunian(self, liunian_gan: str, liunian_zhi: str, year_gan: str = '', day_gan: str = '') -> List[str]:
        """福星贵人 - 大运流年版（a类）"""
        fuxing_map = {
            '甲': ['寅', '子'], '丙': ['寅', '子'],
            '乙': ['卯', '丑'], '癸': ['卯', '丑'],
            '戊': ['申'], '己': ['未'],
            '丁': ['亥'], '庚': ['午'],
            '辛': ['巳'], '壬': ['辰']
        }
        check_gans = [g for g in [year_gan, day_gan] if g]
        for gan in check_gans:
            if gan in fuxing_map and liunian_zhi in fuxing_map.get(gan, []):
                return ['福星贵人']
        return []

    def _check_huagai_dayun_liunian(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """华盖 - 大运流年版（b类）"""
        huagai_map = {
            '寅': '戌', '午': '戌', '戌': '戌',
            '亥': '未', '卯': '未', '未': '未',
            '申': '辰', '子': '辰', '辰': '辰',
            '巳': '丑', '酉': '丑', '丑': '丑'
        }
        for zhi in [day_zhi, year_zhi]:
            if zhi and zhi in huagai_map and liunian_zhi == huagai_map[zhi]:
                return ['华盖']
        return []

    def _check_jiangxing_dayun_liunian(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """将星 - 大运流年版（b类）"""
        jiangxing_map = {
            '寅': '午', '午': '午', '戌': '午',
            '亥': '卯', '卯': '卯', '未': '卯',
            '申': '子', '子': '子', '辰': '子',
            '巳': '酉', '酉': '酉', '丑': '酉'
        }
        for zhi in [day_zhi, year_zhi]:
            if zhi and zhi in jiangxing_map and liunian_zhi == jiangxing_map[zhi]:
                return ['将星']
        return []

    def _check_yima_dayun_liunian(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """驿马 - 大运流年版（b类）"""
        yima_map = {
            '申': '寅', '子': '寅', '辰': '寅',
            '寅': '申', '午': '申', '戌': '申',
            '亥': '巳', '卯': '巳', '未': '巳',
            '巳': '亥', '酉': '亥', '丑': '亥'
        }
        for zhi in [day_zhi, year_zhi]:
            if zhi and zhi in yima_map and liunian_zhi == yima_map[zhi]:
                return ['驿马']
        return []

    def _check_wangshen_dayun_liunian(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """亡神 - 大运流年版（b类）"""
        wangshen_map = {
            '申': '亥', '子': '亥', '辰': '亥',
            '亥': '寅', '卯': '寅', '未': '寅',
            '寅': '巳', '午': '巳', '戌': '巳',
            '巳': '申', '酉': '申', '丑': '申'
        }
        for zhi in [day_zhi, year_zhi]:
            if zhi and zhi in wangshen_map and liunian_zhi == wangshen_map[zhi]:
                return ['亡神']
        return []

    def _check_xianchi_dayun_liunian(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """桃花（原咸池） - 大运流年版（b类）"""
        xianchi_map = {
            '寅': '卯', '午': '卯', '戌': '卯',
            '亥': '子', '卯': '子', '未': '子',
            '申': '酉', '子': '酉', '辰': '酉',
            '巳': '午', '酉': '午', '丑': '午'
        }
        for zhi in [day_zhi, year_zhi]:
            if zhi and zhi in xianchi_map and liunian_zhi == xianchi_map[zhi]:
                return ['桃花']
        return []

    def _check_xueren_dayun_liunian(self, month_zhi: str, liunian_zhi: str) -> List[str]:
        """血刃 - 大运流年版（c类）"""
        xueren_map = {
            '寅': '丑', '卯': '未', '辰': '寅', '巳': '申',
            '午': '卯', '未': '酉', '申': '辰', '酉': '戌',
            '戌': '巳', '亥': '亥', '子': '午', '丑': '子'
        }
        return ['血刃'] if month_zhi in xueren_map and liunian_zhi == xueren_map[month_zhi] else []

    def _check_yuanchen_dayun_liunian(self, liunian_zhi: str, year_zhi: str = '', year_gan: str = '', is_male: bool = True) -> List[str]:
        """
        元辰（大耗）- 大运流年版（f类）
        规则：阳男阴女：子年未，丑年申，寅年酉，卯年戌，辰年亥，巳年子，
              午年丑，未年寅，申年卯，酉年辰，戌年巳，亥年午
              阴男阳女：子年巳，丑年午，寅年未，卯年申，辰年酉，巳年戌，
              午年亥，未年子，申年丑，酉年寅，戌年卯，亥年辰
        补充规则：以年支查大运/流年地支

        参数:
            liunian_zhi: 大运/流年地支
            year_zhi: 原局年支
            year_gan: 原局年干（用于判断阳年阴年）
            is_male: 是否为男性（True-男，False-女）
        """
        if not year_zhi or not liunian_zhi:
            return []

        # 判断年干是阳干还是阴干
        yang_gans = ['甲', '丙', '戊', '庚', '壬']
        is_yang_year = year_gan in yang_gans

        # 元辰映射（阳男阴女）
        yuanchen_yang = {
            '子': '未', '丑': '申', '寅': '酉', '卯': '戌', '辰': '亥', '巳': '子',
            '午': '丑', '未': '寅', '申': '卯', '酉': '辰', '戌': '巳', '亥': '午'
        }

        # 元辰映射（阴男阳女）
        yuanchen_yin = {
            '子': '巳', '丑': '午', '寅': '未', '卯': '申', '辰': '酉', '巳': '戌',
            '午': '亥', '未': '子', '申': '丑', '酉': '寅', '戌': '卯', '亥': '辰'
        }

        # 判断性别和年干组合
        if (is_yang_year and is_male) or (not is_yang_year and not is_male):
            # 阳男阴女
            yuanchen_zhi = yuanchen_yang.get(year_zhi, '')
        else:
            # 阴男阳女
            yuanchen_zhi = yuanchen_yin.get(year_zhi, '')

        return ['元辰'] if liunian_zhi == yuanchen_zhi else []

    def _check_jiesha_dayun_liunian(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """
        劫煞 - 大运流年版（d类）
        原规则：申子辰年/日见巳，亥卯未年/日见申，寅午戌年/日见亥，巳酉丑年/日见寅
        补充规则：以年支/日支查大运/流年地支
        """
        jiesha_map = {
            '申': '巳', '子': '巳', '辰': '巳',
            '亥': '申', '卯': '申', '未': '申',
            '寅': '亥', '午': '亥', '戌': '亥',
            '巳': '寅', '酉': '寅', '丑': '寅'
        }
        # 检查年支和日支
        for zhi in [year_zhi, day_zhi]:
            if zhi and zhi in jiesha_map and liunian_zhi == jiesha_map[zhi]:
                return ['劫煞']
        return []

    def _check_zhaisha_dayun_liunian(self, liunian_zhi: str, year_zhi: str = '', day_zhi: str = '') -> List[str]:
        """
        灾煞 - 大运流年版（d类）
        原规则：申子辰年/日劫煞在巳→灾煞在午；
              寅午戌年/日劫煞在亥→灾煞在子；
              亥卯未年/日劫煞在申→灾煞在酉；
              巳酉丑年/日劫煞在寅→灾煞在卯
        补充规则：以年支/日支查大运/流年地支
        """
        zhaisha_map = {
            '申': '午', '子': '午', '辰': '午',
            '亥': '酉', '卯': '酉', '未': '酉',
            '寅': '子', '午': '子', '戌': '子',
            '巳': '卯', '酉': '卯', '丑': '卯'
        }
        # 检查年支和日支
        for zhi in [year_zhi, day_zhi]:
            if zhi and zhi in zhaisha_map and liunian_zhi == zhaisha_map[zhi]:
                return ['灾煞']
        return []

    def _check_pima_dayun_liunian(self, year_zhi: str, liunian_zhi: str) -> List[str]:
        """披麻 - 大运流年版（d类）"""
        # 披麻规则: 以年支查大运/流年地支
        # 年支：子 丑 寅 卯 辰 巳 午 未 申 酉 戌 亥
        # 披麻：酉 戌 亥 子 丑 寅 卯 辰 巳 午 未 申
        pima_map = {
            '子': '酉', '丑': '戌', '寅': '亥', '卯': '子',
            '辰': '丑', '巳': '寅', '午': '卯', '未': '辰',
            '申': '巳', '酉': '午', '戌': '未', '亥': '申'
        }
        return ['披麻'] if year_zhi in pima_map and liunian_zhi == pima_map[year_zhi] else []

    def _check_sangmen_dayun_liunian(self, year_zhi: str, liunian_zhi: str) -> List[str]:
        """丧门 - 大运流年版（d类）"""
        sangmen_map = {
            '子': '寅', '丑': '卯', '寅': '辰', '卯': '巳',
            '辰': '午', '巳': '未', '午': '申', '未': '酉',
            '申': '戌', '酉': '亥', '戌': '子', '亥': '丑'
        }
        return ['丧门'] if year_zhi in sangmen_map and liunian_zhi == sangmen_map[year_zhi] else []

    def _check_diaoke_dayun_liunian(self, year_zhi: str, liunian_zhi: str) -> List[str]:
        """吊客 - 大运流年版（d类）"""
        diaoke_map = {
            '子': '戌', '丑': '亥', '寅': '子', '卯': '丑',
            '辰': '寅', '巳': '卯', '午': '辰', '未': '巳',
            '申': '午', '酉': '未', '戌': '申', '亥': '酉'
        }
        return ['吊客'] if year_zhi in diaoke_map and liunian_zhi == diaoke_map[year_zhi] else []

    def _check_baihu_dayun_liunian(self, year_zhi: str, liunian_zhi: str) -> List[str]:
        """
        白虎 - 大运流年版（d类）
        原规则：子年见午，丑年见未，寅年见申，卯年见酉，
              辰年见戌，巳年见亥，午年见子，未年见丑，
              申年见寅，酉年见卯，戌年见辰，亥年见巳
        补充规则：以年支查大运/流年地支
        """
        baihu_map = {
            '子': '午', '丑': '未', '寅': '申', '卯': '酉',
            '辰': '戌', '巳': '亥', '午': '子', '未': '丑',
            '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'
        }
        白虎位 = baihu_map.get(year_zhi, '')
        return ['白虎'] if liunian_zhi == 白虎位 else []

    def _check_tiangou_dayun_liunian(self, year_zhi: str, liunian_zhi: str) -> List[str]:
        """
        天狗 - 大运流年版（d类）
        原规则：子年见丑，丑年见寅，寅年见卯，卯年见辰，
              辰年见巳，巳年见午，午年见未，未年见申，
              申年见酉，酉年见戌，戌年见亥，亥年见子
        补充规则：以年支查大运/流年地支
        """
        tiangou_map = {
            '子': '丑', '丑': '寅', '寅': '卯', '卯': '辰',
            '辰': '巳', '巳': '午', '午': '未', '未': '申',
            '申': '酉', '酉': '戌', '戌': '亥', '亥': '子'
        }
        天狗位 = tiangou_map.get(year_zhi, '')
        return ['天狗'] if liunian_zhi == 天狗位 else []

    def _check_tiande_guiREN_dayun_liunian(self, month_zhi: str, liunian_gan: str, liunian_zhi: str) -> List[str]:
        """
        天德贵人 - 大运流年版（e类）
        规则: 正月丁，二月申，三月壬，四月辛，
              五月亥，六月甲，七月癸，八月寅，
              九月丙，十月乙，十一月巳，十二月庚
        
        其中：丁、壬、辛、甲、癸、丙、乙、庚是天干；
              申、亥、寅、巳是地支
        
        补充规则：根据月支判断天德对应的是天干还是地支，
                  然后检查大运/流年对应的天干或地支是否匹配
        """
        # 天德映射: {月支: (类型, 值)}
        # 类型: 'gan'表示天干, 'zhi'表示地支
        tiande_map = {
            '寅': ('gan', '丁'),   # 正月丁
            '卯': ('zhi', '申'),   # 二月申
            '辰': ('gan', '壬'),   # 三月壬
            '巳': ('gan', '辛'),   # 四月辛
            '午': ('zhi', '亥'),   # 五月亥
            '未': ('gan', '甲'),   # 六月甲
            '申': ('gan', '癸'),   # 七月癸
            '酉': ('zhi', '寅'),   # 八月寅
            '戌': ('gan', '丙'),   # 九月丙
            '亥': ('gan', '乙'),   # 十月乙
            '子': ('zhi', '巳'),   # 十一月巳
            '丑': ('gan', '庚')    # 十二月庚
        }
        
        if month_zhi not in tiande_map:
            return []
        
        type_, value = tiande_map[month_zhi]
        
        if type_ == 'gan':
            # 天德对应天干，检查大运/流年天干
            return ['天德贵人'] if liunian_gan == value else []
        else:
            # 天德对应地支，检查大运/流年地支
            return ['天德贵人'] if liunian_zhi == value else []

    def _check_yuede_guiREN_dayun_liunian(self, month_zhi: str, liunian_gan: str) -> List[str]:
        """月德贵人 - 大运流年版（e类）"""
        if month_zhi in ['寅', '午', '戌'] and liunian_gan == '丙':
            return ['月德贵人']
        if month_zhi in ['亥', '卯', '未'] and liunian_gan == '甲':
            return ['月德贵人']
        if month_zhi in ['申', '子', '辰'] and liunian_gan == '壬':
            return ['月德贵人']
        if month_zhi in ['巳', '酉', '丑'] and liunian_gan == '庚':
            return ['月德贵人']
        return []

    def _check_guoyin_dayun_liunian(self, day_gan: str, liunian_zhi: str, year_gan: str = '') -> List[str]:
        """
        国印贵人 - 大运流年版（a类）
        原规则：甲见戌，乙见亥，丙见丑，丁见寅，戊见丑，己见寅，庚见辰，辛见巳，壬见未，癸见申
        补充规则：年干/日干符合 → 再看大运/流年地支
        """
        guoyin_map = {
            '甲': '戌', '乙': '亥', '丙': '丑', '丁': '寅',
            '戊': '丑', '己': '寅', '庚': '辰', '辛': '巳',
            '壬': '未', '癸': '申'
        }
        check_gans = [year_gan, day_gan]
        for gan in check_gans:
            if gan in guoyin_map and liunian_zhi == guoyin_map[gan]:
                return ['国印贵人']
        return []

    def _check_tianchu_dayun_liunian(self, day_gan: str, liunian_zhi: str, year_gan: str = '') -> List[str]:
        """
        天厨贵人 - 大运流年版（a类）
        原规则：甲见巳，乙见午，丙见子，丁见午，戊见申，己见酉，庚见亥，辛见子，壬见寅，癸见卯
        补充规则：年干/日干符合 → 再看大运/流年地支
        """
        tianchu_map = {
            '甲': '巳', '乙': '午', '丙': '子', '丁': '午',
            '戊': '申', '己': '酉', '庚': '亥', '辛': '子',
            '壬': '寅', '癸': '卯'
        }
        check_gans = [year_gan, day_gan]
        for gan in check_gans:
            if gan in tianchu_map and liunian_zhi == tianchu_map[gan]:
                return ['天厨贵人']
        return []

    def _check_xuetang_dayun_liunian(self, day_gan: str, liunian_zhi: str) -> List[str]:
        """
        学堂 - 大运流年版（b类）
        原规则：甲见亥，乙见午，丙见寅，丁见酉，戊见寅，己见酉，庚见巳，辛见子，壬见申，癸见卯
        补充规则：以日干查大运/流年地支
        """
        xuetang_map = {
            '甲': '亥', '乙': '午', '丙': '寅', '丁': '酉',
            '戊': '寅', '己': '酉', '庚': '巳', '辛': '子',
            '壬': '申', '癸': '卯'
        }
        学堂地支 = xuetang_map.get(day_gan, '')
        return ['学堂'] if liunian_zhi == 学堂地支 else []

    def _check_ciguan_dayun_liunian(self, day_gan: str, liunian_zhi: str) -> List[str]:
        """
        词馆 - 大运流年版（b类）
        原规则：甲见寅，乙见卯，丙见巳，丁见午，戊见巳，己见午，庚见申，辛见酉，壬见亥，癸见戌
        补充规则：以日干查大运/流年地支
        """
        ciguan_map = {
            '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
            '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
            '壬': '亥', '癸': '戌'
        }
        词馆地支 = ciguan_map.get(day_gan, '')
        return ['词馆'] if liunian_zhi == 词馆地支 else []

    def _check_lushen_dayun_liunian(self, day_gan: str, liunian_zhi: str) -> List[str]:
        """
        禄神 - 大运流年版（b类）
        原规则：甲禄在寅、乙禄在卯、丙戊禄在巳、丁己禄在午、庚禄在申、辛禄在酉、壬禄在亥、癸禄在子
        补充规则：以日干查大运/流年地支
        """
        lushen_map = {
            '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
            '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
            '壬': '亥', '癸': '子'
        }
        禄位 = lushen_map.get(day_gan, '')
        return ['禄神'] if liunian_zhi == 禄位 else []

    def _check_yangren_dayun_liunian(self, day_gan: str, liunian_zhi: str) -> List[str]:
        """
        羊刃 - 大运流年版（b类）
        原规则：甲日卯，乙日寅，丙日午，丁日巳，戊日午，己日巳，庚日酉，辛日申，壬日子，癸日亥
        补充规则：以日干查大运/流年地支
        """
        yangren_map = {
            '甲': '卯', '乙': '寅', '丙': '午', '丁': '巳',
            '戊': '午', '己': '巳', '庚': '酉', '辛': '申',
            '壬': '子', '癸': '亥'
        }
        羊刃位 = yangren_map.get(day_gan, '')
        return ['羊刃'] if liunian_zhi == 羊刃位 else []

    def _check_liuxia_dayun_liunian(self, day_gan: str, liunian_zhi: str) -> List[str]:
        """
        流霞 - 大运流年版（b类）
        原规则：甲鸡（酉）、乙犬（戌）、丙羊（未）、丁猴（申）、
              戊蛇（巳）、己马（午）、庚龙（辰）、辛兔（卯）、
              壬猪（亥）、癸虎（寅）
        补充规则：以日干查大运/流年地支
        """
        liuxia_map = {
            '甲': '酉', '乙': '戌', '丙': '未', '丁': '申',
            '戊': '巳', '己': '午', '庚': '辰', '辛': '卯',
            '壬': '亥', '癸': '寅'
        }
        流霞位 = liuxia_map.get(day_gan, '')
        return ['流霞'] if liunian_zhi == 流霞位 else []

    def _check_hongyan_sha_dayun_liunian(self, day_gan: str, liunian_zhi: str) -> List[str]:
        """
        红艳煞 - 大运流年版（b类）
        原规则：甲日→午，乙日→午，丙日→寅，丁日→未，戊日→辰，
              己日→辰，庚日→戌，辛日→酉，壬日→子，癸日→申
        补充规则：以日干查大运/流年地支
        """
        hongyan_map = {
            '甲': '午', '乙': '午', '丙': '寅', '丁': '未',
            '戊': '辰', '己': '辰', '庚': '戌', '辛': '酉',
            '壬': '子', '癸': '申'
        }
        红艳位 = hongyan_map.get(day_gan, '')
        return ['红艳煞'] if liunian_zhi == 红艳位 else []

    def _check_tianyi_dayun_liunian(self, month_zhi: str, liunian_zhi: str) -> List[str]:
        """
        天医 - 大运流年版（c类）
        原规则：正月见丑，二月生见寅，三月生见卯，四月生见辰，五月生见巳，六月生见午，七月生见未，八月生见申，九月生见酉，十月生见戌，十一月生见亥，十二月生见子
        补充规则：以月支查大运/流年地支
        """
        tianyi_map = {
            '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
            '午': '巳', '未': '午', '申': '未', '酉': '申',
            '戌': '酉', '亥': '戌', '子': '亥', '丑': '子'
        }
        天医位 = tianyi_map.get(month_zhi, '')
        return ['天医'] if liunian_zhi == 天医位 else []

    def _check_hongluan_dayun_liunian(self, year_zhi: str, liunian_zhi: str) -> List[str]:
        """
        红鸾 - 大运流年版（d类）
        规则: 以年支为基准，对应关系为：
              年支:子丑寅卯辰巳午未申酉戌亥
              三地支见:卯寅丑子亥戌酉申未午已辰
        补充规则：以年支查大运/流年地支
        """
        # 红鸾映射: {年支: 对应地支}
        hongluan_map = {
            '子': '卯', '丑': '寅', '寅': '丑', '卯': '子',
            '辰': '亥', '巳': '戌', '午': '酉', '未': '申',
            '申': '未', '酉': '午', '戌': '巳', '亥': '辰'
        }
        红鸾位 = hongluan_map.get(year_zhi, '')
        return ['红鸾'] if liunian_zhi == 红鸾位 else []

    def _check_tianxi_dayun_liunian(self, year_zhi: str, liunian_zhi: str) -> List[str]:
        """
        天喜 - 大运流年版（d类）
        原规则：年支查其余地支
              子见酉、丑见申、寅见未、卯见午、辰见巳、巳见辰、
              午见卯、未见寅、申见丑、酉见子、戌见亥、亥见戌
        补充规则：以年支查大运/流年地支（一对一映射）
        """
        tianxi_map = {
            '子': '酉', '丑': '申', '寅': '未', '卯': '午',
            '辰': '巳', '巳': '辰', '午': '卯', '未': '寅',
            '申': '丑', '酉': '子', '戌': '亥', '亥': '戌'
        }
        天喜位 = tianxi_map.get(year_zhi, '')
        return ['天喜'] if liunian_zhi == 天喜位 else []

    def _check_goujiao_dayun_liunian(self, liunian_zhi: str, year_zhi: str = '', year_gan: str = '', day_gan: str = '', is_male: bool = True) -> List[str]:
        """
        勾绞煞 - 大运流年版（g类）
        规则: 以年支查大运/流年地支
              子见卯，丑见辰，寅见巳，卯见午，辰见未，巳见申，
              午见酉，未见戌，申见亥，酉见子，戌见丑，亥见寅
        """
        if not year_zhi or not liunian_zhi:
            return []

        # 勾绞煞映射: {年支: 对应地支}
        goujiao_map = {
            '子': '卯', '丑': '辰', '寅': '巳', '卯': '午',
            '辰': '未', '巳': '申', '午': '酉', '未': '戌',
            '申': '亥', '酉': '子', '戌': '丑', '亥': '寅'
        }

        勾绞位 = goujiao_map.get(year_zhi, '')
        return ['勾绞煞'] if liunian_zhi == 勾绞位 else []

    def _check_dexiu_dayun_liunian(self, month_zhi: str, liunian_gan: str) -> List[str]:
        """
        德秀贵人 - 大运流年版（e类）
        原规则：寅午戌月丙丁为德戊癸为秀，申子辰月壬癸戊己为德丙辛甲为秀，巳酉丑月庚辛为德乙庚为秀，亥卯未月甲乙为德丁壬为秀
        补充规则：以月支查大运/流年天干
        """
        if month_zhi in ['寅', '午', '戌']:
            # 寅午戌月：丙丁为德，戊癸为秀
            return ['德秀贵人'] if liunian_gan in ['丙', '丁', '戊', '癸'] else []
        elif month_zhi in ['申', '子', '辰']:
            # 申子辰月：壬癸戊己为德，丙辛甲为秀
            return ['德秀贵人'] if liunian_gan in ['壬', '癸', '戊', '己', '丙', '辛', '甲'] else []
        elif month_zhi in ['巳', '酉', '丑']:
            # 巳酉丑月：庚辛为德，乙庚为秀
            return ['德秀贵人'] if liunian_gan in ['庚', '辛', '乙'] else []
        elif month_zhi in ['亥', '卯', '未']:
            # 亥卯未月：甲乙为德，丁壬为秀
            return ['德秀贵人'] if liunian_gan in ['甲', '乙', '丁', '壬'] else []
        return []

    def _check_tiande_he_dayun_liunian(self, month_zhi: str, liunian_gan: str, liunian_zhi: str) -> List[str]:
        """
        天德合 - 大运流年版（e类）
        原规则：天德所在天干的正五合或地支
        补充规则：以月支查大运/流年天干或地支
        
        根据月支判断天德对应的是天干还是地支，然后检查大运/流年对应的天干或地支是否匹配
        """
        # 天德合映射: {月支: (类型, 值)}
        # 类型: 'gan'表示天干, 'zhi'表示地支
        tiandehe_map = {
            '寅': ('gan', '壬'), '卯': ('zhi', '巳'), '辰': ('gan', '丁'),
            '巳': ('gan', '丙'), '午': ('zhi', '寅'), '未': ('gan', '己'),
            '申': ('gan', '戊'), '酉': ('zhi', '亥'), '戌': ('gan', '辛'),
            '亥': ('gan', '庚'), '子': ('zhi', '申'), '丑': ('gan', '乙')
        }
        if month_zhi not in tiandehe_map:
            return []
        类型, 值 = tiandehe_map[month_zhi]
        if 类型 == 'gan':
            return ['天德合'] if liunian_gan == 值 else []
        else:
            return ['天德合'] if liunian_zhi == 值 else []

    def _check_yuede_he_dayun_liunian(self, month_zhi: str, liunian_gan: str) -> List[str]:
        """
        月德合 - 大运流年版（e类）
        原规则：月德所在天干的正五合（丙→辛，壬→丁，甲→己，庚→乙）
        补充规则：以月支查大运/流年天干
        """
        if month_zhi in ['寅', '午', '戌']:
            月德合天干 = '辛'
        elif month_zhi in ['亥', '卯', '未']:
            月德合天干 = '己'
        elif month_zhi in ['申', '子', '辰']:
            月德合天干 = '丁'
        elif month_zhi in ['巳', '酉', '丑']:
            月德合天干 = '乙'
        else:
            return []
        return ['月德合'] if liunian_gan == 月德合天干 else []

    def _check_yuede_guiREN_dayun_liunian(self, month_zhi: str, liunian_gan: str) -> List[str]:
        """
        月德贵人 - 大运流年版（e类）
        原规则：寅午戌月丙，亥卯未月甲，申子辰月壬，巳酉丑月庚
        补充规则：以月支查大运/流年天干
        """
        if month_zhi in ['寅', '午', '戌']:
            return ['月德贵人'] if liunian_gan == '丙' else []
        elif month_zhi in ['亥', '卯', '未']:
            return ['月德贵人'] if liunian_gan == '甲' else []
        elif month_zhi in ['申', '子', '辰']:
            return ['月德贵人'] if liunian_gan == '壬' else []
        elif month_zhi in ['巳', '酉', '丑']:
            return ['月德贵人'] if liunian_gan == '庚' else []
        return []

    def _check_kongwang_dayun_liunian(self, year_gan: str, year_zhi: str,
                                       liunian_zhi: str, day_gan: str, day_zhi: str) -> List[str]:
        """
        空亡 - 大运流年版（f类）
        原规则：六十甲子每旬剩余两支为空亡
        补充规则：以年干/日干查大运/流年地支是否为该旬的空亡

        空亡判断逻辑（正确版）：
        1. 查年柱所在的旬，获取年柱旬的空亡地支
        2. 查日柱所在的旬，获取日柱旬的空亡地支
        3. 判断大运/流年地支是否在年柱旬的空亡地支或日柱旬的空亡地支中

        说明：空亡以年柱或日柱为基准判断其他柱的地支
        """
        # 定义各旬及其空亡地支
        xunkong_data = [
            # (旬名, 旬中的所有干支组合, 空亡地支)
            ('甲子旬', ['甲子', '乙丑', '丙寅', '丁卯', '戊辰', '己巳', '庚午', '辛未', '壬申', '癸酉'], ('戌', '亥')),
            ('甲戌旬', ['甲戌', '乙亥', '丙子', '丁丑', '戊寅', '己卯', '庚辰', '辛巳', '壬午', '癸未'], ('申', '酉')),
            ('甲申旬', ['甲申', '乙酉', '丙戌', '丁亥', '戊子', '己丑', '庚寅', '辛卯', '壬辰', '癸巳'], ('午', '未')),
            ('甲午旬', ['甲午', '乙未', '丙申', '丁酉', '戊戌', '己亥', '庚子', '辛丑', '壬寅', '癸卯'], ('辰', '巳')),
            ('甲辰旬', ['甲辰', '乙巳', '丙午', '丁未', '戊申', '己酉', '庚戌', '辛亥', '壬子', '癸丑'], ('寅', '卯')),
            ('甲寅旬', ['甲寅', '乙卯', '丙辰', '丁巳', '戊午', '己未', '庚申', '辛酉', '壬戌', '癸亥'], ('子', '丑'))
        ]

        # 构建干支到旬的映射（用于快速查找）
        ganzhi_to_xun = {}
        for xun_name, ganzhi_list, empty_zhis in xunkong_data:
            for ganzhi in ganzhi_list:
                ganzhi_to_xun[ganzhi] = (xun_name, empty_zhis)

        # 查年柱所在的旬
        year_xun_kongwang = None
        if year_gan and year_zhi:
            year_ganzhi = year_gan + year_zhi
            if year_ganzhi in ganzhi_to_xun:
                _, year_xun_kongwang = ganzhi_to_xun[year_ganzhi]

        # 查日柱所在的旬
        day_xun_kongwang = None
        if day_gan and day_zhi:
            day_ganzhi = day_gan + day_zhi
            if day_ganzhi in ganzhi_to_xun:
                _, day_xun_kongwang = ganzhi_to_xun[day_ganzhi]

        # 检查大运/流年地支是否在年柱或日柱的空亡地支中
        if year_xun_kongwang and liunian_zhi in year_xun_kongwang:
            return ['空亡']
        if day_xun_kongwang and liunian_zhi in day_xun_kongwang:
            return ['空亡']

        return []

    def _check_guchengus_dayun_liunian(self, year_zhi: str, liunian_zhi: str) -> List[str]:
        """
        孤辰寡宿 - 大运流年版（f类）
        原规则：亥子丑人孤辰在寅寡宿在戌，寅卯辰人孤辰在巳寡宿在丑，巳午未人孤辰在申寡宿在亥，申酉戌人孤辰在亥寡宿在未
        补充规则：以年支查大运/流年地支
        """
        guchen_map = {
            '亥': '寅', '子': '寅', '丑': '寅',
            '寅': '巳', '卯': '巳', '辰': '巳',
            '巳': '申', '午': '申', '未': '申',
            '申': '亥', '酉': '亥', '戌': '亥'
        }
        gusu_map = {
            '亥': '戌', '子': '戌', '丑': '戌',
            '寅': '丑', '卯': '丑', '辰': '丑',
            '巳': '亥', '午': '亥', '未': '亥',
            '申': '未', '酉': '未', '戌': '未'
        }
        result = []
        年支孤辰 = guchen_map.get(year_zhi, '')
        年支寡宿 = gusu_map.get(year_zhi, '')
        if liunian_zhi == 年支孤辰:
            result.append('孤辰')
        if liunian_zhi == 年支寡宿:
            result.append('寡宿')
        return result

    def _check_tianluo_diwang_dayun_liunian(self, year_zhi: str, day_zhi: str, liunian_zhi: str) -> List[str]:
        """
        天罗地网 - 大运流年版（f类）
        原规则：戌见亥、亥见戌为天罗，辰见巳、巳见辰为地网
        补充规则：以年支/日支查大运/流年地支

        判定逻辑：
        - 年支或日支为戌，流年地支为亥 → 天罗
        - 年支或日支为亥，流年地支为戌 → 天罗
        - 年支或日支为辰，流年地支为巳 → 地网
        - 年支或日支为巳，流年地支为辰 → 地网
        """
        result = []

        # 天罗：戌见亥、亥见戌
        # 检查年支
        if year_zhi == '戌' and liunian_zhi == '亥':
            result.append('天罗地网')
        elif year_zhi == '亥' and liunian_zhi == '戌':
            result.append('天罗地网')
        # 检查日支
        if day_zhi == '戌' and liunian_zhi == '亥':
            result.append('天罗地网')
        elif day_zhi == '亥' and liunian_zhi == '戌':
            result.append('天罗地网')

        # 地网：辰见巳、巳见辰
        # 检查年支
        if year_zhi == '辰' and liunian_zhi == '巳':
            result.append('天罗地网')
        elif year_zhi == '巳' and liunian_zhi == '辰':
            result.append('天罗地网')
        # 检查日支
        if day_zhi == '辰' and liunian_zhi == '巳':
            result.append('天罗地网')
        elif day_zhi == '巳' and liunian_zhi == '辰':
            result.append('天罗地网')

        # 去重
        return list(dict.fromkeys(result))
    
    def get_shensha_details(self, shensha_name: str) -> Optional[Dict]:
        """
        获取神煞的详细信息
        
        参数:
            shensha_name: 神煞名称
            
        返回:
            神煞详细信息的字典,如果不存在则返回None
        """
        info = self.db.get_shensha_info(shensha_name)
        if info:
            return info.to_dict()
        return None
    
    def print_result(self, result: Dict[str, List[str]]):
        """
        打印神煞计算结果
        
        参数:
            result: calculate()方法返回的结果
        """
        print("=" * 60)
        print("八字神煞分析结果")
        print("=" * 60)
        for pillar, shensha_list in result.items():
            if shensha_list:
                print(f"{pillar}: {', '.join(shensha_list)}")
            else:
                print(f"{pillar}: 无")
        print("=" * 60)


def parse_bazi_input(bazi_str: str) -> Dict[str, str]:
    """
    解析八字输入字符串
    
    参数:
        bazi_str: 八字字符串,格式为 "甲子 乙丑 丙寅 丁卯"
                   (年 月 日 时,每柱之间用空格分隔)
        
    返回:
        字典格式: {'year_gan': '甲', 'year_zhi': '子',
                   'month_gan': '乙', 'month_zhi': '丑',
                   'day_gan': '丙', 'day_zhi': '寅',
                   'time_gan': '丁', 'time_zhi': '卯'}
    """
    parts = bazi_str.split()
    
    if len(parts) < 4:
        raise ValueError("八字输入格式错误,需要四柱,格式为: 甲子 乙丑 丙寅 丁卯")
    
    result = {}
    
    # 年柱
    result['year_gan'] = parts[0][0] if len(parts[0]) > 0 else ''
    result['year_zhi'] = parts[0][1] if len(parts[0]) > 1 else ''
    
    # 月柱
    result['month_gan'] = parts[1][0] if len(parts[1]) > 0 else ''
    result['month_zhi'] = parts[1][1] if len(parts[1]) > 1 else ''
    
    # 日柱
    result['day_gan'] = parts[2][0] if len(parts[2]) > 0 else ''
    result['day_zhi'] = parts[2][1] if len(parts[2]) > 1 else ''
    
    # 时柱
    result['time_gan'] = parts[3][0] if len(parts[3]) > 0 else ''
    result['time_zhi'] = parts[3][1] if len(parts[3]) > 1 else ''
    
    return result


def main():
    """主函数: 示例用法"""
    # 创建数据库和计算器
    db = ShenShaDatabase()
    calculator = ShenShaCalculator(db)
    
    # 示例八字: 戊寅 戊午 壬辰 戊申
    bazi_str = "戊寅 戊午 壬辰 戊申"
    
    print(f"输入八字: {bazi_str}")
    print()
    
    # 解析八字
    bazi_dict = parse_bazi_input(bazi_str)
    
    # 计算神煞
    result = calculator.calculate(bazi_dict)
    
    # 打印结果
    calculator.print_result(result)
    
    # 打印详细神煞说明
    print("\n神煞详细信息:")
    print("=" * 60)
    for pillar, shensha_list in result.items():
        if shensha_list:
            for shensha in shensha_list:
                details = calculator.get_shensha_details(shensha)
                if details:
                    print(f"\n【{details['name']}】")
                    print(f"  类别: {details['category']}")
                    print(f"  定义: {details['definition']}")
                    print(f"  喜忌: {details['preference']}")
                    print(f"  形成条件: {details['condition']}")
                    print(f"  说明: {details['explanation']}")
                    print(f"  古籍依据: {details['source']}")


if __name__ == '__main__':
    main()
