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
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">
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

# ... (the rest of the code stays unchanged) ...
