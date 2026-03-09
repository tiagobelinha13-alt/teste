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
    txt = (f'<text x="{w//2}" y="{h//2+font//3}" font-family="sans-serif"'
           f' font-size="{font}" text-anchor="middle" fill="white">{label}</text>') if label else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">
            f'<rect width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"
            f' stroke-width="2" rx="6"/>{txt}</svg>")

def svg_circle(r, fill, label="", font=14):
    d = r*2
    txt = (f'<text x="{r}" y="{r+font//3}" font-family="sans-serif"'
           f' font-size="{font}" text-anchor="middle" fill="white">{label}</text>') if label else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{d}" height="{d}">
            f'<circle cx="{r}" cy="{r}" r="{r-2}" fill="{fill}"
            f' stroke="#000" stroke-width="2"/>{txt}</svg>")

def svg_person(fill="#4a90d9", label=""):
    txt = (f'<text x="25" y="90" font-family="sans-serif" font-size="10"
           f' text-anchor="middle" fill="{fill}">{label}</text>') if label else ""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="95">
        f'<circle cx="25" cy="12" r="11" fill="{fill}" stroke="#000" stroke-width="1.5"/>
        f'<rect x="10" y="24" width="30" height="35" rx="5" fill="{fill}" stroke="#000" stroke-width="1.5"/>
        f'<rect x="13" y="58" width="10" height="28" rx="4" fill="{fill}" stroke="#000" stroke-width="1.5"/>
        f'<rect x="27" y="58" width="10" height="28" rx="4" fill="{fill}" stroke="#000" stroke-width="1.5"/>
        f'{txt}</svg>'
    )

def svg_bg_cover():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360">
        '<rect width="480" height="360" fill="#1a1a2e"/>
        '<text x="240" y="140" font-family="sans-serif" font-size="26" font-weight="bold"
        ' text-anchor="middle" fill="#e94560">Escolhe o Teu Equilibrio</text>
        '<text x="240" y="180" font-family="sans-serif" font-size="18"
        ' text-anchor="middle" fill="#f5a623">Apostas Online</text>
        '<text x="240" y="250" font-family="sans-serif" font-size="13"
        ' text-anchor="middle" fill="#fff">Clica na bandeira verde para comecar</text>
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
        '<text x="220" y="190" font-family="sans-serif" font-size="11" text-anchor="middle" fill="#0f0">BET</text>
        '</svg>'
    )

def svg_bg_escola():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360">
        '<rect width="480" height="360" fill="#87ceeb"/>
        '<rect x="0" y="300" width="480" height="60" fill="#90ee90"/>
        '<rect x="100" y="120" width="280" height="180" fill="#f5f5dc" stroke="#8b8b00" stroke-width="3"/>
        '<rect x="170" y="100" width="140" height="30" fill="#cc0000"/>
        '<text x="240" y="122" font-family="sans-serif" font-size="13" font-weight="bold"
        ' text-anchor="middle" fill="white">ESCOLA</text>
        '<circle cx="420" cy="60" r="30" fill="#FFD700"/>
        '</svg>'
    )

def svg_bg_escuro():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360">
        '<rect width="480" height="360" fill="#050508"/>
        '<text x="240" y="180" font-family="sans-serif" font-size="14"
        ' text-anchor="middle" fill="#440000">madrugada...</text>
        '</svg>'
    )

FALLING_SVG = {
    "Aposta":    (svg_rect(44, 44, "#cc0000", label="BET",  font=14), "mau"),
    "Ficha":     (svg_circle(22, "#8b0000",   label="$$",   font=12), "mau"),
    "Telemovel": (svg_rect(28, 44, "#222", "#888", label="MOB", font=11), "mau"),
    "Livro":     (svg_rect(38, 44, "#1a6b1a",  label="LIV",  font=14), "bom"),
    "Lua":       (svg_circle(22, "#4a4a8a",   label="ZZZ",  font=11), "bom"),
    "Coracao":   (svg_circle(22, "#c0392b",   label="<3",   font=14), "bom"),
}

# ---------------------------------------------------------------------------
# UID + asset helpers
# ---------------------------------------------------------------------------
_uid_counter = [0]
def uid():
    _uid_counter[0] += 1
    random.seed(_uid_counter[0] * 9999991)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

def svg_md5(svg_str):
    b = svg_str.encode("utf-8")
    return hashlib.md5(b).hexdigest(), b

def make_costume(display_name, svg_str, cx=0, cy=0):
    md5, _ = svg_md5(svg_str)
    return {"name": display_name, "bitmapResolution": 1, "dataFormat": "svg",
            "assetId": md5, "md5ext": f"{md5}.svg",
            "rotationCenterX": cx, "rotationCenterY": cy}

# ---------------------------------------------------------------------------
# Block factory
# ---------------------------------------------------------------------------
def blk(opcode, inputs=None, fields=None, next_=None, parent=None,
        top_level=False, x=0, y=0, shadow=False):
    b = {"opcode": opcode, "next": next_, "parent": parent,
         "inputs": inputs or {}, "fields": fields or {},
         "shadow": shadow, "topLevel": top_level}
    if top_level:
        b["x"] = x
        b["y"] = y
    return b

def num(v):     return [1, [4, str(v)]]
def string_(v): return [1, [10, str(v)]]
def sub(bid):   return [2, bid]

# ---------------------------------------------------------------------------
# Broadcast registry
# ---------------------------------------------------------------------------
_BCAST = {}
def bcast_id(name):
    if name not in _BCAST:
        _BCAST[name] = uid()
    return _BCAST[name]

for _n in ["INICIO_JOGO","FASE1","FASE2","DECISAO1","DECISAO2",
           "MOSTRAR_FINAL","APANHOU_APOSTA","APANHOU_LIVRO","APANHOU_SONO"]:
    bcast_id(_n)

def bcast_input(name):
    return [1, [11, name, bcast_id(name)]]

def bcast_field(name):
    return [name, bcast_id(name)]

# ---------------------------------------------------------------------------
# Shadow-block helpers
# ---------------------------------------------------------------------------
def add_keypressed(blocks, key_str, parent_id):
    """sensing_keypressed with a sensing_keyoptions shadow menu."""
    bid = uid()
    sid = uid()
    blocks[sid] = blk("sensing_keyoptions",
                      fields={"KEY_OPTION": [key_str, None]},
                      parent=bid, shadow=True)
    blocks[bid] = blk("sensing_keypressed",
                      inputs={"KEY_OPTION": [1, sid]},
                      parent=parent_id)
    return bid

def add_switch_backdrop(blocks, backdrop_name, next_=None, parent=None):
    """looks_switchbackdropto with a looks_backdrops shadow menu."""
    bid = uid()
    sid = uid()
    blocks[sid] = blk("looks_backdrops",
                      fields={"BACKDROP": [backdrop_name, None]},
                      parent=bid, shadow=True)
    blocks[bid] = blk("looks_switchbackdropto",
                      inputs={"BACKDROP": [1, sid]},
                      next_=next_, parent=parent)
    return bid

def add_touching_kai(blocks, parent_id):
    """sensing_touchingobject checking sprite 'Kai'."""
    menu_id = uid()
    rep_id  = uid()
    blocks[menu_id] = blk("sensing_touchingobjectmenu",
                          fields={"TOUCHINGOBJECTMENU": ["Kai", None]},
                          parent=rep_id, shadow=True)
    blocks[rep_id]  = blk("sensing_touchingobject",
                          inputs={"TOUCHINGOBJECTMENU": [1, menu_id]},
                          parent=parent_id)
    return rep_id

def add_ypos(blocks, parent_id):
    """motion_yposition reporter."""
    bid = uid()
    blocks[bid] = blk("motion_yposition", parent=parent_id)
    return bid

def add_var_reporter(blocks, vname, vid, parent_id):
    bid = uid()
    blocks[bid] = blk("data_variable",
                      fields={"VARIABLE": [vname, vid]},
                      parent=parent_id)
    return bid

# ---------------------------------------------------------------------------
# Chain helper
# ---------------------------------------------------------------------------
def chain(blocks, ids):
    for i, bid in enumerate(ids):
        blocks[bid]["next"]   = ids[i+1] if i+1 < len(ids) else None
        if i > 0:
            blocks[bid]["parent"] = ids[i-1]

# ---------------------------------------------------------------------------
# make_project
# ---------------------------------------------------------------------------
def make_project():
    def nv(name):
        return uid(), name

    v_bem,   nm_bem   = nv("BemEstar")
    v_sono,  nm_sono  = nv("Sono")
    v_notas, nm_notas = nv("Notas")
    v_rel,   nm_rel   = nv("Relacoes")
    v_fase,  nm_fase  = nv("Fase")

    gvars = {
        v_bem:   [nm_bem,   70],
        v_sono:  [nm_sono,  70],
        v_notas: [nm_notas, 70],
        v_rel:   [nm_rel,   70],
        v_fase:  [nm_fase,   0],
    }

    monitors = []
    for vid, vname, mx, my in [
        (v_bem,nm_bem,10,10),(v_sono,nm_sono,10,40),
        (v_notas,nm_notas,10,70),(v_rel,nm_rel,10,100)
    ]:
        monitors.append({"id":vid,"mode":"default","opcode":"data_variable",
                         "params":{"VARIABLE":vname},"spriteName":None,"value":70,
                         "width":0,"height":0,"x":mx,"y":my,"visible":True,
                         "sliderMin":0,"sliderMax":100,"isDiscrete":True})

    # ===== STAGE =====
    stage_blocks = {}
    s_flag = uid()
    inits = []
    for vid, vname, val in [
        (v_bem,nm_bem,70),(v_sono,nm_sono,70),
        (v_notas,nm_notas,70),(v_rel,nm_rel,70),(v_fase,nm_fase,0)
    ]:
        bid = uid()
        stage_blocks[bid] = blk("data_setvariableto",
                                inputs={"VALUE": num(val)},
                                fields={"VARIABLE": [vname, vid]})
        inits.append(bid)

    s_back_id = add_switch_backdrop(stage_blocks, "capa")
    all_inits = inits + [s_back_id]
    chain(stage_blocks, all_inits)
    stage_blocks[s_flag] = blk("event_whenflagclicked", next_=all_inits[0],
                               top_level=True, x=0, y=0)
    stage_blocks[all_inits[0]]["parent"] = s_flag

    # ===== KAI =====
    kai_blocks = {}
    kai_svg     = svg_person("#4a90d9", "Kai")
    kai_svg_sad = svg_person("#888", "Kai")

    # Script A: forever move with arrows
    ka_flag    = uid()
    ka_forever = uid()
    ka_if_r    = uid()
    ka_move_r  = uid()
    ka_if_l    = uid()
    ka_move_l  = uid()
    ka_bounce  = uid()

    key_r = add_keypressed(kai_blocks, "right arrow", ka_if_r)
    kai_blocks[ka_move_r] = blk("motion_changexby", inputs={"DX": num(10)}, parent=ka_if_r)
    kai_blocks[ka_if_r]   = blk("control_if",
                                inputs={"CONDITION": sub(key_r), "SUBSTACK": sub(ka_move_r)},
                                next_=ka_if_l, parent=ka_forever)
    kai_blocks[key_r]["parent"] = ka_if_r

    key_l = add_keypressed(kai_blocks, "left arrow", ka_if_l)
    kai_blocks[ka_move_l] = blk("motion_changexby", inputs={"DX": num(-10)}, parent=ka_if_l)
    kai_blocks[ka_if_l]   = blk("control_if",
                                inputs={"CONDITION": sub(key_l), "SUBSTACK": sub(ka_move_l)},
                                next_=ka_bounce, parent=ka_if_r)
    kai_blocks[key_l]["parent"] = ka_if_l

    kai_blocks[ka_bounce]  = blk("motion_ifonedgebounce", parent=ka_if_l)
    kai_blocks[ka_forever] = blk("control_forever", inputs={"SUBSTACK": sub(ka_if_r)}, parent=ka_flag)
    kai_blocks[ka_flag]    = blk("event_whenflagclicked", next_=ka_forever,
                                 top_level=True, x=20, y=20)

    # Script B: INICIO_JOGO -> intro dialogue -> broadcast FASE1
    kb_recv = uid()
    say_data = [
        ("Ola, eu sou o Kai.", 3),
        ("Tenho andado cansado com a escola e passo demasiado tempo em apostas online.", 4),
        ("Hoje tenho teste amanha e o meu amigo convidou-me outra vez para apostar.", 4),
        ("Vou tentar equilibrar o que faco esta noite...", 3),
    ]
    say_ids = [uid() for _ in say_data]
    kb_bcast_f1 = uid()
    for i, (txt, sec) in enumerate(say_data):
        nxt = say_ids[i+1] if i+1 < len(say_ids) else kb_bcast_f1
        prv = kb_recv if i == 0 else say_ids[i-1]
        kai_blocks[say_ids[i]] = blk("looks_sayforsecs",
                                     inputs={"MESSAGE": string_(txt), "SECS": num(sec)},
                                     next_=nxt, parent=prv)
    kai_blocks[kb_bcast_f1] = blk("event_broadcast",
                                  inputs={"BROADCAST_INPUT": bcast_input("FASE1")},
                                  parent=say_ids[-1])
    kai_blocks[kb_recv] = blk("event_whenbroadcastreceived",
                              fields={"BROADCAST_OPTION": bcast_field("INICIO_JOGO")},
                              next_=say_ids[0], top_level=True, x=400, y=20)

    # Scripts C/D/E: reaction to collected objects
    for rx_name, rx_txt, rx_x in [
        ("APANHOU_APOSTA", "Mais uma aposta... isto esta a fugir do controlo.", 600),
        ("APANHOU_LIVRO",  "Boa, mais tempo de estudo!", 800),
        ("APANHOU_SONO",   "Preciso mesmo de descansar.", 1000),
    ]:
        r = uid(); s = uid()
        kai_blocks[r] = blk("event_whenbroadcastreceived",
                            fields={"BROADCAST_OPTION": bcast_field(rx_name)},
                            next_=s, top_level=True, x=rx_x, y=20)
        kai_blocks[s] = blk("looks_sayforsecs",
                            inputs={"MESSAGE": string_(rx_txt), "SECS": num(2)},
                            parent=r)

    # Script F: MOSTRAR_FINAL -> if/else tree
    kf_recv = uid()

    # negative branch (BemEstar < 40)
    cond_neg  = uid()
    neg_back  = add_switch_backdrop(kai_blocks, "quarto_escuro")
    neg_say   = []
    for txt, sec in [
        ("Passei a noite em apostas online.", 3),
        ("Perdi dinheiro, vou mal preparado para o teste e estou exausto.", 4),
        ("Afastei-me dos amigos e sinto-me preso ao jogo.", 4),
        ("Quando o jogo comeca a controlar a vida, e importante pedir ajuda a alguem de confianca.", 5),
    ]:
        bid = uid()
        kai_blocks[bid] = blk("looks_sayforsecs",
                              inputs={"MESSAGE": string_(txt), "SECS": num(sec)})
        neg_say.append(bid)
    chain(kai_blocks, [neg_back] + neg_say)

    var_r_neg = add_var_reporter(kai_blocks, nm_bem, v_bem, cond_neg)
    kai_blocks[cond_neg] = blk("operator_lt",
                               inputs={"OPERAND1": [3, var_r_neg, [4, "0"]],
                                       "OPERAND2": num(40)})

    # positive branch (BemEstar > 64)
    if_pos   = uid()
    cond_pos = uid()
    pos_back = add_switch_backdrop(kai_blocks, "escola")
    pos_say  = []
    for txt, sec in [
        ("Foi dificil, mas consegui dizer nao as apostas.", 3),
        ("Estudei, descansei e pedi apoio quando precisei.", 3),
        ("Escolher bons habitos e pedir ajuda e um ato de coragem!", 4),
    ]:
        bid = uid()
        kai_blocks[bid] = blk("looks_sayforsecs",
                              inputs={"MESSAGE": string_(txt), "SECS": num(sec)})
        pos_say.append(bid)
    chain(kai_blocks, [pos_back] + pos_say)

    var_r_pos = add_var_reporter(kai_blocks, nm_bem, v_bem, cond_pos)
    kai_blocks[cond_pos] = blk("operator_gt",
                               inputs={"OPERAND1": [3, var_r_pos, [4, "0"]],
                                       "OPERAND2": num(64)})

    # middle branch
    mid_say = []
    for txt, sec in [
        ("Ainda consigo controlar, mas se continuar assim posso perder o equilibrio.", 4),
        ("Tenta de novo e faz escolhas melhores!", 3),
    ]:
        bid = uid()
        kai_blocks[bid] = blk("looks_sayforsecs",
                              inputs={"MESSAGE": string_(txt), "SECS": num(sec)})
        mid_say.append(bid)
    chain(kai_blocks, mid_say)

    # if_pos block
    kai_blocks[if_pos] = blk("control_if_else",
                             inputs={"CONDITION": sub(cond_pos),
                                     "SUBSTACK":  sub(pos_back),
                                     "SUBSTACK2": sub(mid_say[0])})
    kai_blocks[cond_pos]["parent"]  = if_pos
    kai_blocks[pos_back]["parent"]  = if_pos
    kai_blocks[mid_say[0]]["parent"] = if_pos

    # if_neg block
    if_neg = uid()
    kai_blocks[if_neg] = blk("control_if_else",
                             inputs={"CONDITION": sub(cond_neg),
                                     "SUBSTACK":  sub(neg_back),
                                     "SUBSTACK2": sub(if_pos)},
                             parent=kf_recv)
    kai_blocks[cond_neg]["parent"] = if_neg
    kai_blocks[neg_back]["parent"] = if_neg
    kai_blocks[if_pos]["parent"]   = if_neg

    kai_blocks[kf_recv] = blk("event_whenbroadcastreceived",
                              fields={"BROADCAST_OPTION": bcast_field("MOSTRAR_FINAL")},
                              next_=if_neg, top_level=True, x=1200, y=20)

    # ===== CONTROLADOR =====
    ctrl_blocks = {}

    cf    = uid()
    cw    = uid()
    cb_id = add_switch_backdrop(ctrl_blocks, "quarto")
    cbcast = uid()
    ctrl_blocks[cf]    = blk("event_whenflagclicked", next_=cw, top_level=True, x=0, y=0)
    ctrl_blocks[cw]    = blk("control_wait", inputs={"DURATION": num(1)},
                             next_=cb_id, parent=cf)
    ctrl_blocks[cb_id]["next"]   = cbcast
    ctrl_blocks[cb_id]["parent"] = cw
    ctrl_blocks[cbcast] = blk("event_broadcast",
                              inputs={"BROADCAST_INPUT": bcast_input("INICIO_JOGO")},
                              parent=cb_id)

    for recv_n, wait_s, next_n, cx in [
        ("FASE1", 30, "DECISAO1", 200),
        ("FASE2", 25, "DECISAO2", 400),
    ]:
        r = uid(); w = uid(); b = uid()
        ctrl_blocks[r] = blk("event_whenbroadcastreceived",
                             fields={"BROADCAST_OPTION": bcast_field(recv_n)},
                             next_=w, top_level=True, x=cx, y=0)
        ctrl_blocks[w] = blk("control_wait", inputs={"DURATION": num(wait_s)},
                             next_=b, parent=r)
        ctrl_blocks[b] = blk("event_broadcast",
                             inputs={"BROADCAST_INPUT": bcast_input(next_n)},
                             parent=w)

    # ===== AMIGO =====
    amigo_blocks = {}
    amigo_svg = svg_person("#e67e22", "Amigo")

    am_flag = uid(); am_hf = uid()
    amigo_blocks[am_flag] = blk("event_whenflagclicked", next_=am_hf,
                                top_level=True, x=400, y=0)
    amigo_blocks[am_hf] = blk("looks_hide", parent=am_flag)

    for ev, txt, ax in [
        ("DECISAO1", "Estas dentro para recuperar o dinheiro perdido?", 0),
        ("DECISAO2", "Vamos mais uma rodada? E so mais uma vez...", 200),
    ]:
        r = uid(); s = uid(); h = uid()
        amigo_blocks[r] = blk("event_whenbroadcastreceived",
                              fields={"BROADCAST_OPTION": bcast_field(ev)},
                              next_=s, top_level=True, x=ax, y=0)
        amigo_blocks[s] = blk("looks_sayforsecs",
                              inputs={"MESSAGE": string_(txt), "SECS": num(4)},
                              next_=h, parent=r)
        amigo_blocks[h] = blk("looks_hide", parent=s)

    # ===== BUTTON FACTORY =====
    def make_btn_blocks(show_ev, next_ev, var_changes, xpos):
        bb = {}

        # flag -> hide
        f = uid(); fh = uid()
        bb[f]  = blk("event_whenflagclicked", next_=fh, top_level=True, x=0, y=0)
        bb[fh] = blk("looks_hide", parent=f)

        # show_ev -> setx -> sety -> show
        r = uid(); gx = uid(); gy = uid(); sh = uid()
        bb[r]  = blk("event_whenbroadcastreceived",
                     fields={"BROADCAST_OPTION": bcast_field(show_ev)},
                     next_=gx, top_level=True, x=200, y=0)
        bb[gx] = blk("motion_setx", inputs={"X": num(xpos)},  next_=gy, parent=r)
        bb[gy] = blk("motion_sety", inputs={"Y": num(-60)},    next_=sh, parent=gx)
        bb[sh] = blk("looks_show",  parent=gy)

        # click -> var changes -> hide -> broadcast next_ev
        # Build ALL blocks first, then call chain()
        cl = uid()
        bb[cl] = blk("event_whenthisspriteclicked", top_level=True, x=400, y=0)

        change_ids = []
        for (vid, vname, delta) in var_changes:
            cid = uid()
            bb[cid] = blk("data_changevariableby",
                          inputs={"VALUE": num(delta)},
                          fields={"VARIABLE": [vname, vid]})
            change_ids.append(cid)

        hi = uid()
        bc = uid()
        # Add hi and bc to bb BEFORE calling chain()
        bb[hi] = blk("looks_hide")
        bb[bc] = blk("event_broadcast",
                     inputs={"BROADCAST_INPUT": bcast_input(next_ev)});

        click_seq = change_ids + [hi, bc]
        chain(bb, click_seq)
        bb[cl]["next"] = click_seq[0]
        bb[click_seq[0]]["parent"] = cl

        return bb

    btn_specs = [
        ("BtnEstudar",  "#27ae60", "Fechar app e estudar", "DECISAO1", "FASE2",
         [(v_notas,nm_notas,8),(v_sono,nm_sono,5),(v_bem,nm_bem,6)], -80),
        ("BtnApostar1", "#c0392b", "Entrar nas apostas",   "DECISAO1", "FASE2",
         [(v_bem,nm_bem,-10),(v_sono,nm_sono,-8),(v_notas,nm_notas,-10)], 80),
        ("BtnDormir",   "#27ae60", "Desligar e ir dormir", "DECISAO2", "MOSTRAR_FINAL",
         [(v_sono,nm_sono,12),(v_bem,nm_bem,10),(v_notas,nm_notas,8)], -80),
        ("BtnApostar2", "#c0392b", "Continuar ate tarde",  "DECISAO2", "MOSTRAR_FINAL",
         [(v_bem,nm_bem,-15),(v_sono,nm_sono,-20),(v_notas,nm_notas,-12),(v_rel,nm_rel,-8)], 80),
    ]

    # ===== FALLING OBJECTS =====
    falling_sprites = []
    for obj_name, (obj_svg, obj_type) in FALLING_SVG.items():
        fb = {}

        if obj_type == "mau":
            vd = [(v_bem,nm_bem,-8),(v_sono,nm_sono,-5),(v_notas,nm_notas,-7),(v_rel,nm_rel,-5)]
            bh = "APANHOU_APOSTA"
        else:
            vd_map = {
                "Livro":   [(v_notas,nm_notas,10),(v_bem,nm_bem,6)],
                "Lua":     [(v_sono,nm_sono,12), (v_bem,nm_bem,6)],
                "Coracao": [(v_rel,nm_rel,10),   (v_bem,nm_bem,6)],
            }
            vd = vd_map.get(obj_name, [])
            bh_map = {"Livro":"APANHOU_LIVRO","Lua":"APANHOU_SONO","Coracao":"APANHOU_LIVRO"}
            bh = bh_map.get(obj_name, "APANHOU_LIVRO")

        of = uid(); oh = uid()
        fb[of] = blk("event_whenflagclicked", next_=oh, top_level=True, x=0, y=0)
        fb[oh] = blk("looks_hide", parent=of)

        def make_fall(recv_ev, sx, blocks_out, _vd=vd, _bh=bh):
            r     = uid(); show  = uid(); set_x = uid(); set_y = uid()
            frev  = uid(); move_y= uid(); if_touch = uid()
            var_ids = [uid() for _ in _vd]
            bc_hit= uid(); hide_t= uid(); wait_t= uid()
            if_bot= uid(); cond_bot= uid(); rx2= uid(); ry2= uid()

            # Build all blocks first (no forward references in chain)
            blocks_out[r]      = blk("event_whenbroadcastreceived",
                                     fields={"BROADCAST_OPTION": bcast_field(recv_ev)},
                                     next_=show, top_level=True,
                                     x=0 if recv_ev == "FASE1" else 300, y=200)
            blocks_out[show]   = blk("looks_show",  next_=set_x, parent=r)
            blocks_out[set_x]  = blk("motion_setx", inputs={"X": num(sx)},
                                     next_=set_y, parent=show)
            blocks_out[set_y]  = blk("motion_sety", inputs={"Y": num(170)},
                                     next_=frev, parent=set_x)

            blocks_out[move_y] = blk("motion_changeyby", inputs={"DY": num(-4)},
                                     next_=if_touch, parent=frev)

            touch_cond = add_touching_kai(blocks_out, if_touch)

            # var change chain inside touch substack
            for i, (vid, vname, delta) in enumerate(_vd):
                nxt = var_ids[i+1] if i+1 < len(var_ids) else bc_hit
                prv = if_touch if i == 0 else var_ids[i-1]
                blocks_out[var_ids[i]] = blk("data_changevariableby",
                                             inputs={"VALUE": num(delta)},
                                             fields={"VARIABLE": [vname, vid]},
                                             next_=nxt, parent=prv)

            first_sub = var_ids[0] if var_ids else bc_hit
            blocks_out[bc_hit]  = blk("event_broadcast",
                                      inputs={"BROADCAST_INPUT": bcast_input(_bh)},
                                      next_=hide_t,
                                      parent=var_ids[-1] if var_ids else if_touch)
            blocks_out[hide_t]  = blk("looks_hide",  next_=wait_t, parent=bc_hit)
            # wait_t loops back to set_x (reposition at top)
            blocks_out[wait_t]  = blk("control_wait", inputs={"DURATION": num(1)},
                                      next_=set_x, parent=hide_t)

            blocks_out[if_touch] = blk("control_if",
                                       inputs={"CONDITION": sub(touch_cond),
                                               "SUBSTACK":  sub(first_sub)},
                                       next_=if_bot, parent=move_y)
            blocks_out[touch_cond]["parent"] = if_touch

            # y < -170 bottom reset
            ypos = add_ypos(blocks_out, cond_bot)
            blocks_out[cond_bot] = blk("operator_lt",
                                       inputs={"OPERAND1": [3, ypos, [4, "0"],
                                               "OPERAND2": num(-170)},
                                       parent=if_bot)
            blocks_out[rx2] = blk("motion_setx", inputs={"X": num(sx)},
                                  next_=ry2, parent=if_bot)
            blocks_out[ry2] = blk("motion_sety", inputs={"Y": num(170)}, parent=rx2)

            blocks_out[if_bot] = blk("control_if",
                                     inputs={"CONDITION": sub(cond_bot),
                                             "SUBSTACK":  sub(rx2)},
                                     parent=if_touch)
            blocks_out[frev]   = blk("control_forever",
                                     inputs={"SUBSTACK": sub(move_y)},
                                     parent=set_y)

        bx = random.randint(-180, 150)
        make_fall("FASE1", bx,      fb)
        make_fall("FASE2", bx + 30, fb)
        falling_sprites.append((obj_name, obj_svg, fb))

    # ===== ASSEMBLE project =====
    ctrl_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2"/>'

    def sprite(name, svg_str, blocks_dict, layer, vis, x, y, sz,
               cx=25, cy=47, rot="all around", extra_costumes=None):
        costumes = [make_costume(name.lower(), svg_str, cx, cy)]
        if extra_costumes:
            costumes += extra_costumes
        return {
            "isStage": False, "name": name,
            "variables": {}, "lists": {}, "broadcasts": {},
            "blocks": blocks_dict, "comments": {},
            "currentCostume": 0, "costumes": costumes,
            "sounds": [], "volume": 100, "layerOrder": layer,
            "visible": vis, "x": x, "y": y, "size": sz,
            "direction": 90, "draggable": False, "rotationStyle": rot,
        }

    stage_target = {
        "isStage": True, "name": "Stage",
        "variables": {vid: [vname, val] for vid, (vname, val) in gvars.items()},
        "lists": {}, "broadcasts": {bid: bname for bname, bid in _BCAST.items()},
        "blocks": stage_blocks, "comments": {}, "currentCostume": 0,
        "costumes": [
            make_costume("capa",          svg_bg_cover(),  240, 180),
            make_costume("quarto",        svg_bg_quarto(), 240, 180),
            make_costume("escola",        svg_bg_escola(), 240, 180),
            make_costume("quarto_escuro", svg_bg_escuro(), 240, 180),
        ],
        "sounds": [], "volume": 100, "layerOrder": 0,
        "tempo": 60, "videoTransparency": 50, "videoState": "off",
        "textToSpeechLanguage": None,
    }

    sprites_list = [
        sprite("Kai", kai_svg, kai_blocks, 2, True, 0, -130, 80,
               cx=25, cy=47, rot="left-right",
               extra_costumes=[make_costume("kai_sad", kai_svg_sad, 25, 47)]),
        sprite("Controlador", ctrl_svg, ctrl_blocks, 1, False, 0, 0, 1,
               cx=1, cy=1),
        sprite("Amigo", amigo_svg, amigo_blocks, 3, False, 150, -80, 80,
               cx=25, cy=47),
    ]

    for i, (bname, bfill, blabel, show_ev, next_ev, bvars, bxpos) in enumerate(btn_specs):
        bsvg    = svg_rect(120, 44, bfill, label=blabel, font=11)
        bblocks = make_btn_blocks(show_ev, next_ev, bvars, bxpos)
        sprites_list.append(
            sprite(bname, bsvg, bblocks, 4+i, False, bxpos, -60, 100,
                   cx=60, cy=22, rot="all around")
        )

    for i, (oname, osvg, oblocks) in enumerate(falling_sprites):
        sprites_list.append(
            sprite(oname, osvg, oblocks, 8+i, False, 0, 170, 70,
                   cx=22, cy=22)
        )

    return {
        "targets": [stage_target] + sprites_list,
        "monitors": monitors,
        "extensions": [],
        "meta": {"semver": "3.0.0", "vm": "0.2.0", "agent": "PythonGen/3.0"},
    }


# ---------------------------------------------------------------------------
# Build .sb3
# ---------------------------------------------------------------------------
def build_sb3(out="equilibrio_apostas.sb3"):
    project = make_project()

    svgs = {
        "capa":          svg_bg_cover(),
        "quarto":        svg_bg_quarto(),
        "escola":        svg_bg_escola(),
        "quarto_escuro": svg_bg_escuro(),
        "kai":           svg_person("#4a90d9", "Kai"),
        "kai_sad":       svg_person("#888", "Kai"),
        "amigo":         svg_person("#e67e22", "Amigo"),
        "controlador":   '<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2"/>',
        "BtnEstudar":    svg_rect(120, 44, "#27ae60", label="Fechar app e estudar", font=11),
        "BtnApostar1":   svg_rect(120, 44, "#c0392b", label="Entrar nas apostas",   font=11),
        "BtnDormir":     svg_rect(120, 44, "#27ae60", label="Desligar e ir dormir", font=11),
        "BtnApostar2":   svg_rect(120, 44, "#c0392b", label="Continuar ate tarde",  font=11),
    }
    for oname, (osvg, _) in FALLING_SVG.items():
        svgs[oname] = osvg

    asset_map = {}
    for svg_str in svgs.values():
        md5, bts = svg_md5(svg_str)
        asset_map[md5] = bts

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("project.json", json.dumps(project, ensure_ascii=False))
        for md5, bts in asset_map.items():
            zf.writestr(f"{md5}.svg", bts)

    print(f"OK  {out}  ({os.path.getsize(out):,} bytes)")
    print("   Carrega em scratch.mit.edu -> Ficheiro -> Carregar do teu computador")


if __name__ == "__main__":
    build_sb3()