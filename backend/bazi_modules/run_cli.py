#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字命理分析系统 - 启动脚本
直接运行此脚本启动命令行版本
"""

import sys
import os

# 确保当前目录在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bazi_cli import main

if __name__ == '__main__':
    main()
