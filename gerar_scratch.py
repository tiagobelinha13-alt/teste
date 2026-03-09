#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gerar_scratch.py
Gera o ficheiro escolhe_equilibrio.sb3 (projeto Scratch 3 valido).
Uso: python gerar_scratch.py
"""

import json
import zipfile
import hashlib
import random
import string
import io


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def uid():
    """Gera UID de 20 chars alfanumericos (estilo Scratch)."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=20))

def svg_rect(text, fill, width=96, height=64):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
        f'<rect width="{width}" height="{height}" fill="{fill}" rx="8"/>'
        f'<text x="{width//2}" y="{height//2+6}" text-anchor="middle" '
        f'font-family="Arial" font-size="13" font-weight="bold" fill="white">{text}</text>'
        f'</svg>'
    )

def svg_backdrop(fill, width=480, height=360):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
        f'<rect width="{width}" height="{height}" fill="{fill}"/>'
        f'</svg>'
    )

def make_costume(name, svg_text, cx=48, cy=32):
    svg_bytes = svg_text.encode('utf-8')
    md5 = hashlib.md5(svg_bytes).hexdigest()
    filename = md5 + '.svg'
    costume = {
        "assetId": md5,
        "name": name,
        "md5ext": filename,
        "dataFormat": "svg",
        "bitmapResolution": 1,
        "rotationCenterX": cx,
        "rotationCenterY": cy
    }
    return costume, filename, svg_bytes

def blk(opcode, next_id=None, parent_id=None, inputs=None,
        fields=None, top_level=False, x=0, y=0, shadow=False, mutation=None):
    b = {
        "opcode": opcode,
        "next": next_id,
        "parent": parent_id,
        "inputs": inputs or {},
        "fields": fields or {},
        "shadow": shadow,
        "topLevel": top_level,
    }
    if top_level:
        b["x"] = x
        b["y"] = y
    if mutation is not None:
        b["mutation"] = mutation
    return b

# ---------------------------------------------------------------------------
# IDs de variaveis e broadcasts (fixos)
# ---------------------------------------------------------------------------

VAR = {
    "BemEstar":    uid(),
    "Sono":        uid(),
    "Notas":       uid(),
    "Relacoes":    uid(),
    "Fase":        uid(),
    "DecisaoFlag": uid(),
}

MSG = {
    "iniciar_jogo1":    uid(),
    "iniciar_jogo2":    uid(),
    "parar_objetos":    uid(),
    "mostrar_decisao1": uid(),
    "mostrar_decisao2": uid(),
    "escolha_boa_1":    uid(),
    "escolha_ma_1":     uid(),
    "escolha_boa_2":    uid(),
    "escolha_ma_2":     uid(),
}  

# ---------------------------------------------------------------------------
# Construtores de blocos atomicos
# ---------------------------------------------------------------------------

def b_set_var(blocks, vname, value, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("data_setvariableto", next_id, parent_id,
                      inputs={"VALUE": [1, [10, str(value)]]},
                      fields={"VARIABLE": [vname, VAR[vname]]})
    return bid

def b_change_var(blocks, vname, value, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("data_changevariableby", next_id, parent_id,
                      inputs={"VALUE": [1, [4, str(value)]]},
                      fields={"VARIABLE": [vname, VAR[vname]]})
    return bid

def b_wait(blocks, secs, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("control_wait", next_id, parent_id,
                      inputs={"DURATION": [1, [5, str(secs)]]})
    return bid

def b_say_for_secs(blocks, text, secs, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("looks_sayforsecs", next_id, parent_id,
                      inputs={"MESSAGE": [1, [10, text]], "SECS": [1, [4, str(secs)]]})
    return bid

def b_backdrop(blocks, name, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("looks_switchbackdropto", next_id, parent_id,
                      inputs={"BACKDROP": [1, [11, name, "_random_"]]})
    return bid

def b_broadcast(blocks, mname, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("event_broadcast", next_id, parent_id,
                      inputs={"BROADCAST_INPUT": [1, [11, mname, MSG[mname]]]})
    return bid

def b_goto_xy(blocks, x, y, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("motion_gotoxy", next_id, parent_id,
                      inputs={"X": [1, [4, str(x)]], "Y": [1, [4, str(y)]]})
    return bid

def b_show(blocks, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("looks_show", next_id, parent_id)
    return bid

def b_hide(blocks, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("looks_hide", next_id, parent_id)
    return bid

def b_stop_this(blocks, parent_id=None):
    bid = uid()
    blocks[bid] = blk("control_stop", None, parent_id,
                      fields={"STOP_OPTION": ["this script", None]},
                      mutation={"tagName": "mutation", "children": [], "hasnext": "false"})
    return bid

def b_change_x(blocks, dx, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("motion_changexby", next_id, parent_id,
                      inputs={"DX": [1, [4, str(dx)]]})
    return bid

def b_change_y(blocks, dy, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("motion_changeyby", next_id, parent_id,
                      inputs={"DY": [1, [4, str(dy)]]})
    return bid

def b_set_y(blocks, y, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("motion_sety", next_id, parent_id,
                      inputs={"Y": [1, [4, str(y)]]})
    return bid

def b_set_x_random(blocks, lo, hi, next_id=None, parent_id=None):
    rand_id = uid()
    sx_id = uid()
    blocks[rand_id] = blk("operator_random", None, sx_id,
                          inputs={"FROM": [1, [4, str(lo)]], "TO": [1, [4, str(hi)]]})
    blocks[sx_id] = blk("motion_setx", next_id, parent_id,
                        inputs={"X": [3, rand_id, [4, "0"]]})
    return sx_id

def make_var_block(blocks, vname, parent_id):
    bid = uid()
    blocks[bid] = blk("data_variable", None, parent_id,
                      fields={"VARIABLE": [vname, VAR[vname]]})
    return bid

def make_lt_block(blocks, vname, value, parent_id):
    lt_id = uid()
    var_id = uid()
    blocks[var_id] = blk("data_variable", None, lt_id,
                         fields={"VARIABLE": [vname, VAR[vname]]})
    blocks[lt_id] = blk("operator_lt", None, parent_id,
                        inputs={
                            "OPERAND1": [3, var_id, [10, ""]],
                            "OPERAND2": [1, [10, str(value)]]
                        })
    return lt_id

def make_ge_block(blocks, vname, value, parent_id):
    """NOT (var < value)"""
    not_id = uid()
    lt_id = uid()
    var_id = uid()
    blocks[var_id] = blk("data_variable", None, lt_id,
                         fields={"VARIABLE": [vname, VAR[vname]]})
    blocks[lt_id] = blk("operator_lt", None, not_id,
                        inputs={
                            "OPERAND1": [3, var_id, [10, ""]],
                            "OPERAND2": [1, [10, str(value)]]
                        })
    blocks[not_id] = blk("operator_not", None, parent_id,
                         inputs={"OPERAND": [2, lt_id]})
    return not_id

def make_or_block(blocks, left_id, right_id, parent_id):
    bid = uid()
    blocks[bid] = blk("operator_or", None, parent_id,
                      inputs={"OPERAND1": [2, left_id], "OPERAND2": [2, right_id]})
    blocks[left_id]["parent"] = bid
    blocks[right_id]["parent"] = bid
    return bid

def make_and_block(blocks, left_id, right_id, parent_id):
    bid = uid()
    blocks[bid] = blk("operator_and", None, parent_id,
                      inputs={"OPERAND1": [2, left_id], "OPERAND2": [2, right_id]})
    blocks[left_id]["parent"] = bid
    blocks[right_id]["parent"] = bid
    return bid

def make_eq_block(blocks, vname, value, parent_id):
    eq_id = uid()
    var_id = uid()
    blocks[var_id] = blk("data_variable", None, eq_id,
                         fields={"VARIABLE": [vname, VAR[vname]]})
    blocks[eq_id] = blk("operator_equals", None, parent_id,
                        inputs={
                            "OPERAND1": [3, var_id, [10, ""]],
                            "OPERAND2": [1, [10, str(value)]]
                        })
    return eq_id

def make_not_eq_block(blocks, vname, value, parent_id):
    not_id = uid()
    eq_id = make_eq_block(blocks, vname, value, not_id)
    blocks[not_id] = blk("operator_not", None, parent_id,
                         inputs={"OPERAND": [2, eq_id]})
    return not_id

def b_wait_until(blocks, cond_id, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("control_wait_until", next_id, parent_id,
                      inputs={"CONDITION": [2, cond_id]})
    blocks[cond_id]["parent"] = bid
    return bid

def b_if(blocks, cond_id, substack_id, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("control_if", next_id, parent_id,
                      inputs={"CONDITION": [2, cond_id], "SUBSTACK": [2, substack_id]})
    blocks[cond_id]["parent"] = bid
    blocks[substack_id]["parent"] = bid
    return bid

def b_if_else(blocks, cond_id, sub1_id, sub2_id, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("control_if_else", next_id, parent_id,
                      inputs={"CONDITION": [2, cond_id],
                               "SUBSTACK": [2, sub1_id],
                               "SUBSTACK2": [2, sub2_id]})
    blocks[cond_id]["parent"] = bid
    blocks[sub1_id]["parent"] = bid
    blocks[sub2_id]["parent"] = bid
    return bid


def b_forever(blocks, substack_id, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("control_forever", next_id, parent_id,
                      inputs={"SUBSTACK": [2, substack_id]})
    blocks[substack_id]["parent"] = bid
    return bid

def b_repeat(blocks, times, substack_id, next_id=None, parent_id=None):
    bid = uid()
    blocks[bid] = blk("control_repeat", next_id, parent_id,
                      inputs={"TIMES": [1, [6, str(times)]], "SUBSTACK": [2, substack_id]})
    blocks[substack_id]["parent"] = bid
    return bid

def chain(blocks, block_ids):
    """Liga lista de IDs em cadeia next/parent."""
    for i, bid in enumerate(block_ids):
        blocks[bid]["next"] = block_ids[i + 1] if i + 1 < len(block_ids) else None
        if i > 0:
            blocks[bid]["parent"] = block_ids[i - 1]

# ---------------------------------------------------------------------------
# Assets globais
# ---------------------------------------------------------------------------

all_assets = {}

# ---------------------------------------------------------------------------
# Stage
# ---------------------------------------------------------------------------

def make_stage():
    blocks = {}
    costumes = []
    backdrops = [
        ("Capa",         svg_backdrop("#1a1a4e"), 240, 180),
        ("Quarto",       svg_backdrop("#2d1b4e"), 240, 180),
        ("Escola",       svg_backdrop("#a5d6a7"), 240, 180),
        ("QuartoEscuro", svg_backdrop("#000000"), 240, 180),
    ]
    for name, svg, cx, cy in backdrops:
        c, fn, fb = make_costume(name, svg, cx, cy)
        costumes.append(c)
        all_assets[fn] = fb

    variables = {VAR[k]: [k, 70 if k not in ("Fase", "DecisaoFlag") else 0]
                 for k in VAR}
    broadcasts = {MSG[k]: k for k in MSG}

    monitors = []
    positions = [(5, 5), (5, 35), (5, 65), (5, 95)]
    visible_vars = ["BemEstar", "Sono", "Notas", "Relacoes"]
    for i, vname in enumerate(visible_vars):
        mx, my = positions[i]
        monitors.append({
            "id": VAR[vname],
            "mode": "default",
            "opcode": "data_variable",
            "params": {"VARIABLE": vname},
            "spriteName": None,
            "value": 70,
            "width": 0, "height": 0,
            "x": mx, "y": my,
            "visible": True,
            "sliderMin": 0, "sliderMax": 100,
            "isDiscrete": True
        })

    return {
        "isStage": True,
        "name": "Stage",
        "variables": variables,
        "lists": {},
        "broadcasts": broadcasts,
        "blocks": blocks,
        "comments": {},
        "currentCostume": 0,
        "costumes": costumes,
        "sounds": [],
        "volume": 100,
        "layerOrder": 0,
        "tempo": 60,
        "videoTransparency": 50,
        "videoState": "off",
        "textToSpeechLanguage": None
    }, monitors

# ---------------------------------------------------------------------------
# Sprite Kai
# ---------------------------------------------------------------------------

def make_kai():
    blocks = {}
    svg = svg_rect("KAI", "#1565C0", 80, 50)
    c, fn, fb = make_costume("Kai", svg, 40, 25)
    all_assets[fn] = fb

    s1 = uid()  # event_whenflagclicked

    sv1 = b_set_var(blocks, "BemEstar", 70)
    sv2 = b_set_var(blocks, "Sono", 70)
    sv3 = b_set_var(blocks, "Notas", 70)
    sv4 = b_set_var(blocks, "Relacoes", 70)
    sv5 = b_set_var(blocks, "Fase", 0)
    sv6 = b_set_var(blocks, "DecisaoFlag", 0)

    bd_capa   = b_backdrop(blocks, "Capa")
    w1        = b_wait(blocks, 3)
    bd_quarto = b_backdrop(blocks, "Quarto")
    gt        = b_goto_xy(blocks, 0, -130)
    sh        = b_show(blocks)
    d1 = b_say_for_secs(blocks, "Ola, eu sou o Kai.", 3)
    d2 = b_say_for_secs(blocks, "Tenho andado cansado com a escola e passo demasiado tempo em apostas online.", 4)
    d3 = b_say_for_secs(blocks, "Hoje tenho teste amanha e o meu amigo convidou-me outra vez para apostar.", 4)
    d4 = b_say_for_secs(blocks, "Vou tentar equilibrar o que faco esta noite...", 3)
    br1  = b_broadcast(blocks, "iniciar_jogo1")
    w2   = b_wait(blocks, 20)
    bp1  = b_broadcast(blocks, "parar_objetos")
    bmd1 = b_broadcast(blocks, "mostrar_decisao1")

    cond1 = make_not_eq_block(blocks, "DecisaoFlag", "0", None)
    wu1   = b_wait_until(blocks, cond1)

    chN1  = b_change_var(blocks, "Notas", 8)
    chS1  = b_change_var(blocks, "Sono", 5)
    chBE1 = b_change_var(blocks, "BemEstar", 5)
    chain(blocks, [chN1, chS1, chBE1])

    chBE1m = b_change_var(blocks, "BemEstar", -10)
    chS1m  = b_change_var(blocks, "Sono", -8)
    chR1m  = b_change_var(blocks, "Relacoes", -5)
    chain(blocks, [chBE1m, chS1m, chR1m])

    ceq1    = make_eq_block(blocks, "DecisaoFlag", "1", None)
    if_dec1 = b_if_else(blocks, ceq1, chN1, chBE1m)

    sv_df0 = b_set_var(blocks, "DecisaoFlag", 0)
    br2    = b_broadcast(blocks, "iniciar_jogo2")
    w3     = b_wait(blocks, 20)
    bp2    = b_broadcast(blocks, "parar_objetos")
    bmd2   = b_broadcast(blocks, "mostrar_decisao2")

    cond2 = make_not_eq_block(blocks, "DecisaoFlag", "0", None)
    wu2   = b_wait_until(blocks, cond2)

    chSo2  = b_change_var(blocks, "Sono", 10)
    chBE2  = b_change_var(blocks, "BemEstar", 8)
    chRe2  = b_change_var(blocks, "Relacoes", 5)
    chain(blocks, [chSo2, chBE2, chRe2])

    chBE2m = b_change_var(blocks, "BemEstar", -15)
    chSo2m = b_change_var(blocks, "Sono", -12)
    chNo2m = b_change_var(blocks, "Notas", -10)
    chain(blocks, [chBE2m, chSo2m, chNo2m])

    ceq2    = make_eq_block(blocks, "DecisaoFlag", "1", None)
    if_dec2 = b_if_else(blocks, ceq2, chSo2, chBE2m)

    # Finais
    lt_be  = make_lt_block(blocks, "BemEstar", 30, None)
    lt_sn  = make_lt_block(blocks, "Sono", 30, None)
    lt_no  = make_lt_block(blocks, "Notas", 40, None)
    or1    = make_or_block(blocks, lt_be, lt_sn, None)
    or_neg = make_or_block(blocks, or1, lt_no, None)

    bd_dark = b_backdrop(blocks, "QuartoEscuro")
    fn1 = b_say_for_secs(blocks, "Passei a noite em apostas online.", 3)
    fn2 = b_say_for_secs(blocks, "Perdi dinheiro, vou mal preparado para o teste e estou exausto.", 4)
    fn3 = b_say_for_secs(blocks, "Afastei-me dos amigos e sinto-me preso ao jogo.", 4)
    fn4 = b_say_for_secs(blocks, "Quando o jogo controla a vida, pede ajuda a alguem de confianca.", 5)
    chain(blocks, [bd_dark, fn1, fn2, fn3, fn4])

    ge_be   = make_ge_block(blocks, "BemEstar", 70, None)
    ge_sn   = make_ge_block(blocks, "Sono", 60, None)
    ge_no   = make_ge_block(blocks, "Notas", 60, None)
    and1    = make_and_block(blocks, ge_be, ge_sn, None)
    and_pos = make_and_block(blocks, and1, ge_no, None)

    bd_escola = b_backdrop(blocks, "Escola")
    fp1 = b_say_for_secs(blocks, "Foi dificil, mas consegui dizer nao as apostas!", 3)
    fp2 = b_say_for_secs(blocks, "Estudei, descansei e pedi apoio quando precisei.", 4)
    fp3 = b_say_for_secs(blocks, "Sinto-me mais confiante e com mais energia.", 3)
    fp4 = b_say_for_secs(blocks, "Escolher bons habitos e pedir ajuda e um acto de coragem!", 5)
    chain(blocks, [bd_escola, fp1, fp2, fp3, fp4])

    fi1 = b_say_for_secs(blocks, "Ainda consigo controlar, mas se continuar assim posso perder o equilibrio.", 5)

    if_pos = b_if_else(blocks, and_pos, bd_escola, fi1)
    if_neg = b_if_else(blocks, or_neg, bd_dark, if_pos)

    w_end   = b_wait(blocks, 1)
    say_end = b_say_for_secs(blocks, "Clica na bandeira verde para jogar de novo e experimentar outras escolhas!", 5)

    main_chain = [
        sv1, sv2, sv3, sv4, sv5, sv6,
        bd_capa, w1, bd_quarto, gt, sh,
        d1, d2, d3, d4,
        br1, w2, bp1, bmd1, wu1, if_dec1,
        sv_df0, br2, w3, bp2, bmd2, wu2, if_dec2,
        if_neg, w_end, say_end
    ]
    chain(blocks, main_chain)

    blocks[s1] = blk("event_whenflagclicked", main_chain[0], None,
                     top_level=True, x=0, y=0)
    blocks[main_chain[0]]["parent"] = s1

    # Scripts de movimento
    for msg_name, tx in [("iniciar_jogo1", 300), ("iniciar_jogo2", 600)]:
        top_id = uid()

        rk_menu = uid()
        rk_id   = uid()
        blocks[rk_menu] = blk("sensing_keyoptions", None, rk_id,
                              fields={"KEY_OPTION": ["right arrow", None]}, shadow=True)
        blocks[rk_id] = blk("sensing_keypressed", None, None,
                            inputs={"KEY_OPTION": [1, rk_menu]})
        cx_r = b_change_x(blocks, 10)
        if_r = b_if(blocks, rk_id, cx_r)
        blocks[rk_id]["parent"] = if_r

        lk_menu = uid()
        lk_id   = uid()
        blocks[lk_menu] = blk("sensing_keyoptions", None, lk_id,
                              fields={"KEY_OPTION": ["left arrow", None]}, shadow=True)
        blocks[lk_id] = blk("sensing_keypressed", None, None,
                            inputs={"KEY_OPTION": [1, lk_menu]})
        cx_l = b_change_x(blocks, -10)
        if_l = b_if(blocks, lk_id, cx_l)
        blocks[lk_id]["parent"] = if_l

        chain(blocks, [if_r, if_l])
        forever_id = b_forever(blocks, if_r)

        blocks[top_id] = blk("event_whenbroadcastreceived", forever_id, None,
                             fields={"BROADCAST_OPTION": [msg_name, MSG[msg_name]]},
                             top_level=True, x=tx, y=0)
        blocks[forever_id]["parent"] = top_id

    return {
        "isStage": False,
        "name": "Kai",
        "variables": {}, "lists": {}, "broadcasts": {},
        "blocks": blocks, "comments": {},
        "currentCostume": 0, "costumes": [c], "sounds": [],
        "volume": 100, "layerOrder": 1, "visible": True,
        "x": 0, "y": -130, "size": 100, "direction": 90,
        "draggable": False, "rotationStyle": "left-right"
    }

# ---------------------------------------------------------------------------
# Sprite Amigo
# ---------------------------------------------------------------------------

def make_amigo():
    blocks = {}
    svg = svg_rect("AMIGO", "#2E7D32", 96, 64)
    c, fn, fb = make_costume("Amigo", svg, 48, 32)
    all_assets[fn] = fb

    top_id = uid()
    sh  = b_show(blocks)
    gt  = b_goto_xy(blocks, -80, 50)
    say = b_say_for_secs(blocks, "Estas dentro para recuperar o dinheiro perdido?", 4)
    hid = b_hide(blocks)
    chain(blocks, [sh, gt, say, hid])
    blocks[top_id] = blk("event_whenbroadcastreceived", sh, None,
                         fields={"BROADCAST_OPTION": ["mostrar_decisao1", MSG["mostrar_decisao1"]]},
                         top_level=True, x=0, y=0)
    blocks[sh]["parent"] = top_id

    top2 = uid()
    hid2 = b_hide(blocks)
    blocks[top2] = blk("event_whenflagclicked", hid2, None, top_level=True, x=200, y=0)
    blocks[hid2]["parent"] = top2

    return {
        "isStage": False,
        "name": "Amigo",
        "variables": {}, "lists": {}, "broadcasts": {},
        "blocks": blocks, "comments": {},
        "currentCostume": 0, "costumes": [c], "sounds": [],
        "volume": 100, "layerOrder": 2, "visible": False,
        "x": -80, "y": 50, "size": 100, "direction": 90,
        "draggable": False, "rotationStyle": "all around"
    }

# ---------------------------------------------------------------------------
# Sprites de objectos que caem
# ---------------------------------------------------------------------------

def make_falling_object(name, svg_color, label, layer,
                        changes1, changes2, offset_secs=0, reps1=12, reps2=16):
    blocks = {}
    svg = svg_rect(label, svg_color, 70, 45)
    c, fn, fb = make_costume(name, svg, 35, 22)
    all_assets[fn] = fb

    def one_fall(changes_dict):
        sy_reset = b_set_y(blocks, -200)
        ch_ids = []
        for vn, delta in changes_dict.items():
            ch_ids.append(b_change_var(blocks, vn, delta))
        if ch_ids:
            chain(blocks, ch_ids + [sy_reset])
            first_ch = ch_ids[0]
        else:
            first_ch = sy_reset

        touch_menu = uid()
        touch_id   = uid()
        blocks[touch_menu] = blk("sensing_touchingobjectmenu", None, touch_id,
                                 fields={"TOUCHINGOBJECTMENU": ["Kai", None]}, shadow=True)
        blocks[touch_id] = blk("sensing_touchingobject", None, None,
                               inputs={"TOUCHINGOBJECTMENU": [1, touch_menu]})
        if_touch = b_if(blocks, touch_id, first_ch)
        blocks[touch_id]["parent"] = if_touch

        cy_id = b_change_y(blocks, -8)
        chain(blocks, [cy_id, if_touch])
        rep_inner = b_repeat(blocks, 45, cy_id)

        sy_top  = b_set_y(blocks, 170)
        sx_rand = b_set_x_random(blocks, -200, 200)
        chain(blocks, [sx_rand, sy_top, rep_inner])
        return sx_rand

    def fall_script(top_msg, tx, ty, reps, changes, offset=0):
        top_id = uid()
        sh = b_show(blocks)
        chain_ids = [sh]

        if offset > 0:
            w_off = b_wait(blocks, offset)
            chain_ids.append(w_off)

        fall_starts = [one_fall(changes) for _ in range(reps)]
        chain(blocks, fall_starts)
        hid = b_hide(blocks)
        chain(blocks, [fall_starts[-1], hid])
        chain_ids.append(fall_starts[0])
        chain(blocks, chain_ids)

        blocks[top_id] = blk("event_whenbroadcastreceived", chain_ids[0], None,
                             fields={"BROADCAST_OPTION": [top_msg, MSG[top_msg]]},
                             top_level=True, x=tx, y=ty)
        blocks[chain_ids[0]]["parent"] = top_id

    fall_script("iniciar_jogo1", 0,   0, reps1, changes1, offset=0)
    fall_script("iniciar_jogo2", 300, 0, reps2, changes2, offset=offset_secs)

    top_stop = uid()
    hid_stop = b_hide(blocks)
    blocks[top_stop] = blk("event_whenbroadcastreceived", hid_stop, None,
                           fields={"BROADCAST_OPTION": ["parar_objetos", MSG["parar_objetos"]]},
                           top_level=True, x=600, y=0)
    blocks[hid_stop]["parent"] = top_stop

    top_flag = uid()
    hid_flag = b_hide(blocks)
    blocks[top_flag] = blk("event_whenflagclicked", hid_flag, None,
                           top_level=True, x=900, y=0)
    blocks[hid_flag]["parent"] = top_flag

    return {
        "isStage": False,
        "name": name,
        "variables": {}, "lists": {}, "broadcasts": {},
        "blocks": blocks, "comments": {},
        "currentCostume": 0, "costumes": [c], "sounds": [],
        "volume": 100, "layerOrder": layer, "visible": False,
        "x": 0, "y": 170, "size": 100, "direction": 90,
        "draggable": False, "rotationStyle": "all around"
    }

# ---------------------------------------------------------------------------
# Botoes de decisao
# ---------------------------------------------------------------------------

def make_button(name, label, svg_color, bx, by, layer, good):
    blocks = {}
    svg = svg_rect(label, svg_color, 140, 55)
    c, fn, fb = make_costume(name, svg, 70, 27)
    all_assets[fn] = fb

    for msg_name, tx in [("mostrar_decisao1", 0), ("mostrar_decisao2", 300)]:
        top_id = uid()
        gt = b_goto_xy(blocks, bx, by)
        sh = b_show(blocks)
        chain(blocks, [gt, sh])
        blocks[top_id] = blk("event_whenbroadcastreceived", gt, None,
                             fields={"BROADCAST_OPTION": [msg_name, MSG[msg_name]]},
                             top_level=True, x=tx, y=0)
        blocks[gt]["parent"] = top_id

    top_click = uid()
    sv_df = b_set_var(blocks, "DecisaoFlag", 1 if good else 2)
    hid   = b_hide(blocks)
    chain(blocks, [sv_df, hid])
    blocks[top_click] = blk("event_whenthisspriteclicked", sv_df, None,
                            top_level=True, x=600, y=0)
    blocks[sv_df]["parent"] = top_click

    top_flag = uid()
    hid_flag = b_hide(blocks)
    blocks[top_flag] = blk("event_whenflagclicked", hid_flag, None,
                           top_level=True, x=900, y=0)
    blocks[hid_flag]["parent"] = top_flag

    return {
        "isStage": False,
        "name": name,
        "variables": {}, "lists": {}, "broadcasts": {},
        "blocks": blocks, "comments": {},
        "currentCostume": 0, "costumes": [c], "sounds": [],
        "volume": 100, "layerOrder": layer, "visible": False,
        "x": bx, "y": by, "size": 100, "direction": 90,
        "draggable": False, "rotationStyle": "all around"
    }

# ---------------------------------------------------------------------------
# Sprite TextoDecisao
# ---------------------------------------------------------------------------

def make_texto_decisao():
    blocks = {}
    svg = svg_rect("?", "#616161", 320, 60)
    c, fn, fb = make_costume("TextoDecisao", svg, 160, 30)
    all_assets[fn] = fb

    for msg_name, text, tx in [
        ("mostrar_decisao1",
         "Amigo: 'Estas dentro para recuperar o dinheiro perdido?'", 0),
        ("mostrar_decisao2",
         "Ja e tarde. Continuas a apostar ou vais dormir/pedir ajuda?", 300),
    ]:
        top_id = uid()
        sh  = b_show(blocks)
        gt  = b_goto_xy(blocks, 0, 80)
        say = b_say_for_secs(blocks, text, 20)
        hid = b_hide(blocks)
        chain(blocks, [sh, gt, say, hid])
        blocks[top_id] = blk("event_whenbroadcastreceived", sh, None,
                             fields={"BROADCAST_OPTION": [msg_name, MSG[msg_name]]},
                             top_level=True, x=tx, y=0)
        blocks[sh]["parent"] = top_id

    top_flag = uid()
    hid_flag = b_hide(blocks)
    blocks[top_flag] = blk("event_whenflagclicked", hid_flag, None,
                           top_level=True, x=600, y=0)
    blocks[hid_flag]["parent"] = top_flag

    return {
        "isStage": False,
        "name": "TextoDecisao",
        "variables": {}, "lists": {}, "broadcasts": {},
        "blocks": blocks, "comments": {},
        "currentCostume": 0, "costumes": [c], "sounds": [],
        "volume": 100, "layerOrder": 8, "visible": False,
        "x": 0, "y": 80, "size": 100, "direction": 90,
        "draggable": False, "rotationStyle": "all around"
    }

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    stage, monitors = make_stage()
    kai   = make_kai()
    amigo = make_amigo()

    aposta = make_falling_object(
        "ObjetoAposta", "#C62828", "BET", 3,
        changes1={"BemEstar": -5, "Sono": -3, "Notas": -4, "Relacoes": -3},
        changes2={"BemEstar": -6, "Sono": -4, "Notas": -5, "Relacoes": -4},
        reps1=12, reps2=16
    )
    ficha = make_falling_object(
        "ObjetoFicha", "#E65100", "FICHA", 4,
        changes1={"BemEstar": -4, "Sono": -4, "Notas": -3, "Relacoes": -4},
        changes2={"BemEstar": -5, "Sono": -5, "Notas": -4, "Relacoes": -5},
        offset_secs=1.5, reps1=10, reps2=14
    )
    livro = make_falling_object(
        "ObjetoLivro", "#2E7D32", "LIVRO", 5,
        changes1={"Notas": 7, "BemEstar": 5},
        changes2={"Notas": 8, "BemEstar": 6},
        offset_secs=1.0, reps1=10, reps2=13
    )
    sono_obj = make_falling_object(
        "ObjetoSono", "#1565C0", "SONO", 6,
        changes1={"Sono": 8, "BemEstar": 3},
        changes2={"Sono": 9, "BemEstar": 4},
        offset_secs=2.0, reps1=8, reps2=11
    )
    amigos_obj = make_falling_object(
        "ObjetoAmigos", "#AD1457", "AMIGOS", 7,
        changes1={"Relacoes": 7, "BemEstar": 4},
        changes2={"Relacoes": 8, "BemEstar": 5},
        offset_secs=3.0, reps1=7, reps2=10
    )

    btn_verde    = make_button("BotaoVerde",    "SIM OK", "#388E3C", -90, -60, 9,  True)
    btn_vermelho = make_button("BotaoVermelho", "NAO",    "#C62828",  90, -60, 10, False)
    texto_dec    = make_texto_decisao()

    targets = [
        stage, kai, amigo,
        aposta, ficha, livro, sono_obj, amigos_obj,
        btn_verde, btn_vermelho, texto_dec
    ]

    project = {
        "targets": targets,
        "monitors": monitors,
        "extensions": [],
        "meta": {"semver": "3.0.0", "vm": "0.2.0", "agent": ""}
    }

    output_path = "escolhe_equilibrio.sb3"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for filename, data in all_assets.items():
            zf.writestr(filename, data)
        zf.writestr("project.json", json.dumps(project, ensure_ascii=False))

    with open(output_path, "wb") as f:
        f.write(buf.getvalue())

    print(f"Ficheiro '{output_path}' criado com sucesso!")
    print("Carrega-o em https://scratch.mit.edu  (Ficheiro > Carregar do teu computador)")
    print("Clica na bandeira verde para jogar!")

if __name__ == "__main__":
    main()