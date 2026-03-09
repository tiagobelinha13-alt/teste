#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera equilibrio_apostas.sb3 - Scratch 3 valido.
Execute: python3 gerar_scratch.py
"""

import json, zipfile, os, hashlib, random, string

# ---------------------------------------------------------------------------
# SVG helpers
# ---------------------------------------------------------------------------
def svg_rect(w, h, fill, stroke="#000", label="", font=14):
    txt = (f'<text x="{w//2}" y="{h//2+font//3}" font-family="sans-serif"
           f' font-size="{font}" text-anchor="middle" fill="white">{label}</text>') if label else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">'
            f'<rect width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"
            f' stroke-width="2" rx="6"/>{txt}</svg>")

def svg_circle(r, fill, label="", font=14):
    d = r * 2
    txt = (f'<text x="{r}" y="{r+font//3}" font-family="sans-serif"
           f' font-size="{font}" text-anchor="middle" fill="white">{label}</text>') if label else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{d}" height="{d}">
            f'<circle cx="{r}" cy="{r}" r="{r-2}" fill="{fill}"
            f' stroke="#000" stroke-width="2"/>{txt}</svg>")

def svg_person(fill="#4a90d9", label=""):
    txt = (f'<text x="25" y="90" font-family="sans-serif" font-size="10"
           f' text-anchor="middle" fill="{fill}">{label}</text>') if label else ""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="95">
        + f'<circle cx="25" cy="12" r="11" fill="{fill}" stroke="#000" stroke-width="1.5"/>
        + f'<rect x="10" y="24" width="30" height="35" rx="5" fill="{fill}" stroke="#000" stroke-width="1.5"/>
        + f'<rect x="13" y="58" width="10" height="28" rx="4" fill="{fill}" stroke="#000" stroke-width="1.5"/>
        + f'<rect x="27" y="58" width="10" height="28" rx="4" fill="{fill}" stroke="#000" stroke-width="1.5"/>
        + txt
        + '</svg>'
    )

def svg_bg_cover():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360">
        '<rect width="480" height="360" fill="#1a1a2e"/>
        '<text x="240" y="140" font-family="sans-serif" font-size="26" font-weight="bold"
        ' text-anchor="middle" fill="#e94560">Escolhe o Teu Equilibrio</text>'
        '<text x="240" y="180" font-family="sans-serif" font-size="18"
        ' text-anchor="middle" fill="#f5a623">Apostas Online</text>'
        '<text x="240" y="250" font-family="sans-serif" font-size="13"
        ' text-anchor="middle" fill="#fff">Clica na bandeira verde para comecar</text>'
        '</svg>'
    )

def svg_bg_quarto():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360">
        '<rect width="480" height="360" fill="#0d1b2a"/>
        '<rect x="0" y="300" width="480" height="60" fill="#2c1810"/>
        '<circle cx="90" cy="30" r="20" fill="#fffacd"/>
        '<rect x="160" y="150" width="120" height="70" fill="#1c1c1c" stroke="#444" stroke-width="2" rx="4"/>
        '<rect x="165" y="155" width="110" height="60" fill="#0a3060"/>
        '<text x="220" y="190" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#0f0">BET</text>'
        '</svg>'
    )

# ... rest of the file content remains the same ... 

