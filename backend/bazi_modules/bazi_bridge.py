"""
Bazi Bridge - Python 桥接脚本
供 Android Kotlin 层通过 Chaquopy 调用
"""
import json
import traceback


def analyze_bazi_unified(year, month, day, hour, minute, is_male, liunian_year, 
                         name="", province_city="", use_true_solar_time=False,
                         include_database=True, include_basic_paipan=True):
    """
    统一的八字分析入口函数
    
    所有分析操作（正常输入、历史记录、真太阳时、无时辰等）都通过此函数执行
    
    Args:
        year: 出生年 (int)
        month: 出生月 (int)
        day: 出生日 (int)
        hour: 出生时 (int or None, None表示时辰未知)
        minute: 出生分 (int, 用于真太阳时计算)
        is_male: 是否男性 (bool)
        liunian_year: 流年年份 (int)
        name: 姓名 (str, 可选)
        province_city: 出生地，格式为"省份 城市" (str, 可选)
        use_true_solar_time: 是否使用真太阳时 (bool)
        include_database: 是否包含数据库详细解析 (bool)
        include_basic_paipan: 是否包含基本排盘数据 (bool)
        
    Returns:
        字典格式的分析结果
    """
    from lunar_python import Solar, Lunar
    from bazi_geju_refactored_v5 import GeJuAnalyzerV5
    from true_solar_time import convert_to_true_solar_time_for_bazi, format_true_solar_time_result
    
    # 保存原始时间
    original_datetime = {
        'year': int(year),
        'month': int(month),
        'day': int(day),
        'hour': int(hour) if hour is not None else None,
        'minute': int(minute)
    }
    
    # 真太阳时计算结果
    true_solar_result = None
    
    # 如果使用真太阳时且提供了出生地，进行转换
    if use_true_solar_time and province_city and hour is not None:
        true_solar_result = convert_to_true_solar_time_for_bazi(
            int(year), int(month), int(day),
            int(hour), int(minute),
            province_city
        )
        
        if true_solar_result:
            # 使用真太阳时进行八字计算
            year = true_solar_result['year']
            month = true_solar_result['month']
            day = true_solar_result['day']
            hour = true_solar_result['hour']
    
    # 1. 日期转八字
    if hour is not None:
        solar = Solar.fromYmdHms(int(year), int(month), int(day), int(hour), 0, 0)
    else:
        solar = Solar.fromYmd(int(year), int(month), int(day))

    lunar = solar.getLunar()
    ba = lunar.getEightChar()

    bazi_dict = {
        'year_gan': ba.getYearGan(),
        'year_zhi': ba.getYearZhi(),
        'month_gan': ba.getMonthGan(),
        'month_zhi': ba.getMonthZhi(),
        'day_gan': ba.getDayGan(),
        'day_zhi': ba.getDayZhi(),
        'time_gan': ba.getTimeGan() if hour is not None else '',
        'time_zhi': ba.getTimeZhi() if hour is not None else '',
    }

    # 2. 构建 birth_date 字符串
    birth_date = f"{int(year)}-{int(month):02d}-{int(day):02d}"
    if hour is not None:
        birth_date += f" {int(hour):02d}:00"

    # 3. 创建分析器并执行分析
    analyzer = GeJuAnalyzerV5(
        bazi=bazi_dict,
        liunian_year=int(liunian_year),
        is_male=bool(is_male),
        birth_date=birth_date
    )
    
    # 设置姓名（用于输出）
    if name:
        analyzer.user_name = name
    
    result = analyzer.analyze()

    # 4. 获取完整的打印数据
    complete_data = analyzer.get_complete_print_data()
    
    # 5. 获取数据库详细解析（如果需要）
    if include_database:
        try:
            database_analysis = analyzer.get_database_analysis()
            print(f"[DEBUG] bazi_bridge: database_analysis type: {type(database_analysis)}")
            print(f"[DEBUG] bazi_bridge: database_analysis keys: {database_analysis.keys() if isinstance(database_analysis, dict) else 'Not a dict'}")
            if '错误' in database_analysis:
                print(f"[DEBUG] bazi_bridge: Error in database_analysis: {database_analysis['错误']}")
            complete_data['数据库解析'] = database_analysis
            if '特殊流年分析' in database_analysis:
                print(f"[DEBUG] bazi_bridge: 特殊流年分析 found")
                print(f"[DEBUG] bazi_bridge: 流年伏吟: {database_analysis['特殊流年分析'].get('流年伏吟', [])}")
            else:
                print(f"[DEBUG] bazi_bridge: 特殊流年分析 NOT found in database_analysis")
        except Exception as e:
            print(f"[DEBUG] bazi_bridge: Error getting database analysis: {e}")
            import traceback
            traceback.print_exc()
    
    # 设置姓名
    if name:
        complete_data['基本信息']['姓名'] = name

    # 6. 构建返回结果
    output = {
        'success': True,
        'bazi': bazi_dict,
        'bazi_display': {
            'year': bazi_dict['year_gan'] + bazi_dict['year_zhi'],
            'month': bazi_dict['month_gan'] + bazi_dict['month_zhi'],
            'day': bazi_dict['day_gan'] + bazi_dict['day_zhi'],
            'time': (bazi_dict['time_gan'] + bazi_dict['time_zhi']) if hour is not None else '未知',
        },
        'complete_data': complete_data,
        'analysis': result,
        'original_datetime': original_datetime,
        'use_true_solar_time': use_true_solar_time,
        'province_city': province_city,
    }
    
    # 添加基本排盘数据（如果需要）
    if include_basic_paipan:
        output['basic_paipan'] = {
            '基本信息': complete_data['基本信息'],
            '四柱': complete_data['四柱']
        }
    
    # 添加真太阳时信息
    if true_solar_result:
        output['true_solar_time'] = {
            'original_time': true_solar_result['original_time'],
            'true_solar_time': true_solar_result['true_solar_time'],
            'longitude_diff': true_solar_result['longitude_diff'],
            'equation_of_time': true_solar_result['equation_of_time'],
            'total_diff': true_solar_result['total_diff'],
            'longitude': true_solar_result['longitude'],
            'latitude': true_solar_result['latitude'],
            'formatted_result': format_true_solar_time_result(true_solar_result)
        }
    
    return output


def get_city_list():
    """
    获取所有城市列表（用于下拉选择）

    Returns:
        JSON字符串，包含省份和城市列表
    """
    try:
        from city_database import get_cities_by_province, get_city_list

        result = {
            'success': True,
            'city_list': get_city_list(),
            'cities_by_province': get_cities_by_province()
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


def get_provinces_list():
    """
    获取所有省份列表

    Returns:
        JSON字符串，包含省份列表
    """
    try:
        from city_database import get_provinces

        result = {
            'success': True,
            'provinces': get_provinces()
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


def get_cities_by_province_name(province_name):
    """
    根据省份名称获取城市列表

    Args:
        province_name: 省份名称

    Returns:
        JSON字符串，包含该省所有城市
    """
    try:
        from city_database import get_cities_by_province_name

        cities = get_cities_by_province_name(province_name)
        result = {
            'success': True,
            'province': province_name,
            'cities': cities
        }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


def get_province_by_city_name(city_name):
    """
    根据城市名称获取所属省份

    Args:
        city_name: 城市名称

    Returns:
        JSON字符串，包含省份信息
    """
    try:
        from city_database import get_province_by_city_name

        province = get_province_by_city_name(city_name)
        if province:
            result = {
                'success': True,
                'city': city_name,
                'province': province
            }
        else:
            result = {
                'success': False,
                'error': f'找不到城市: {city_name}'
            }
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


def calculate_true_solar_time(year, month, day, hour, minute, province_city):
    """
    计算真太阳时
    
    Args:
        year: 年 (int)
        month: 月 (int)
        day: 日 (int)
        hour: 时 (int)
        minute: 分 (int)
        province_city: 格式为"省份 城市"的字符串
        
    Returns:
        JSON字符串，包含真太阳时计算结果
    """
    try:
        from true_solar_time import convert_to_true_solar_time_for_bazi, format_true_solar_time_result
        
        result = convert_to_true_solar_time_for_bazi(
            int(year), int(month), int(day), 
            int(hour), int(minute), 
            province_city
        )
        
        if result is None:
            return json.dumps({
                'success': False, 
                'error': '找不到该城市，请检查城市名称'
            }, ensure_ascii=False)
        
        # 添加格式化后的字符串
        result['formatted_result'] = format_true_solar_time_result(result)
        result['success'] = True
        
        return json.dumps(result, ensure_ascii=False, default=str)
        
    except Exception as e:
        error_output = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return json.dumps(error_output, ensure_ascii=False)


def analyze_bazi_with_true_solar_time(year, month, day, hour, minute, is_male, liunian_year, province_city, use_true_solar_time=False):
    """
    执行八字排盘分析（支持真太阳时）
    统一调用 analyze_bazi_unified 函数
    
    Args:
        year: 出生年 (int)
        month: 出生月 (int)
        day: 出生日 (int)
        hour: 出生时 (int)
        minute: 出生分 (int)
        is_male: 是否男性 (bool)
        liunian_year: 流年年份 (int)
        province_city: 出生地，格式为"省份 城市"的字符串
        use_true_solar_time: 是否使用真太阳时 (bool)
        
    Returns:
        JSON 字符串，包含完整分析结果
    """
    try:
        output = analyze_bazi_unified(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            is_male=is_male,
            liunian_year=liunian_year,
            name="",
            province_city=province_city,
            use_true_solar_time=use_true_solar_time,
            include_database=True,
            include_basic_paipan=True
        )
        return json.dumps(output, ensure_ascii=False, default=str)

    except Exception as e:
        error_output = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return json.dumps(error_output, ensure_ascii=False)


def analyze_bazi(year, month, day, hour, is_male, liunian_year):
    """
    执行八字排盘分析（不通过真太阳时）
    统一调用 analyze_bazi_unified 函数

    Args:
        year: 出生年 (int)
        month: 出生月 (int)
        day: 出生日 (int)
        hour: 出生时 (int or None, None表示不知道时辰)
        is_male: 是否男性 (bool)
        liunian_year: 流年年份 (int)

    Returns:
        JSON 字符串，包含完整分析结果
    """
    try:
        output = analyze_bazi_unified(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=0,
            is_male=is_male,
            liunian_year=liunian_year,
            name="",
            province_city="",
            use_true_solar_time=False,
            include_database=True,
            include_basic_paipan=False
        )
        return json.dumps(output, ensure_ascii=False, default=str)

    except Exception as e:
        error_output = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return json.dumps(error_output, ensure_ascii=False)


def get_bazi_only(year, month, day, hour):
    """
    仅获取八字四柱信息（快速预览）
    """
    try:
        from lunar_python import Solar

        if hour is not None:
            solar = Solar.fromYmdHms(int(year), int(month), int(day), int(hour), 0, 0)
        else:
            solar = Solar.fromYmd(int(year), int(month), int(day))

        lunar = solar.getLunar()
        ba = lunar.getEightChar()

        result = {
            'success': True,
            'year': ba.getYearGan() + ba.getYearZhi(),
            'month': ba.getMonthGan() + ba.getMonthZhi(),
            'day': ba.getDayGan() + ba.getDayZhi(),
            'time': (ba.getTimeGan() + ba.getTimeZhi()) if hour is not None else '未知',
        }
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)


def get_basic_paipan(year, month, day, hour, is_male, liunian_year):
    """
    获取基本排盘界面的结构化数据
    统一调用 analyze_bazi_unified 函数
    
    Args:
        year: 出生年 (int)
        month: 出生月 (int)
        day: 出生日 (int)
        hour: 出生时 (int or None)
        is_male: 是否男性 (bool)
        liunian_year: 流年年份 (int)
    
    Returns:
        JSON字符串，包含基本排盘所需的所有结构化数据
    """
    try:
        from lunar_python import Solar, Lunar
        
        output = analyze_bazi_unified(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=0,
            is_male=is_male,
            liunian_year=liunian_year,
            name="",
            province_city="",
            use_true_solar_time=False,
            include_database=False,
            include_basic_paipan=True
        )
        
        # 添加农历和阳历信息
        if hour is not None:
            solar = Solar.fromYmdHms(int(year), int(month), int(day), int(hour), 0, 0)
        else:
            solar = Solar.fromYmd(int(year), int(month), int(day))
        lunar = solar.getLunar()
        ba = solar.getLunar().getEightChar()
        
        if 'basic_paipan' in output and '基本信息' in output['basic_paipan']:
            output['basic_paipan']['基本信息']['农历'] = f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}{ba.getTimeZhi() if hour is not None else ''}时"
            output['basic_paipan']['基本信息']['阳历'] = f"{int(year)}年{int(month):02d}月{int(day):02d}日 {int(hour) if hour is not None else '未知'}:00"

        return json.dumps(output, ensure_ascii=False, default=str)

    except Exception as e:
        error_output = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return json.dumps(error_output, ensure_ascii=False)


def get_complete_analysis(year, month, day, hour, is_male, liunian_year, name=""):
    """
    获取完整的八字分析数据（包含大运流年、干支图示等）
    统一调用 analyze_bazi_unified 函数
    
    Args:
        year: 出生年 (int)
        month: 出生月 (int)
        day: 出生日 (int)
        hour: 出生时 (int or None)
        is_male: 是否男性 (bool)
        liunian_year: 流年年份 (int)
        name: 姓名 (str)
    
    Returns:
        JSON字符串，包含完整的分析数据结构
    """
    try:
        output = analyze_bazi_unified(
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=0,
            is_male=is_male,
            liunian_year=liunian_year,
            name=name,
            province_city="",
            use_true_solar_time=False,
            include_database=True,
            include_basic_paipan=True
        )
        return json.dumps(output, ensure_ascii=False, default=str)

    except Exception as e:
        error_output = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return json.dumps(error_output, ensure_ascii=False)
