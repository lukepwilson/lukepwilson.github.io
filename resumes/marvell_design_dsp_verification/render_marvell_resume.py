import cairo

WIDTH, HEIGHT = 612, 792
LEFT, RIGHT = 38, 574
CONTENT_W = RIGHT - LEFT
LINE_GAP = 4
BULLET_X = 62
TEXT_X = 82

surface = cairo.PDFSurface('/home/luke-w/Desktop/resumes/marvell_resume_marvell_technology.pdf', WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.set_source_rgb(0, 0, 0)


def set_font(family='Latin Modern Roman', size=10.5, slant=cairo.FONT_SLANT_NORMAL, weight=cairo.FONT_WEIGHT_NORMAL):
    ctx.select_font_face(family, slant, weight)
    ctx.set_font_size(size)


def text_width(text):
    return ctx.text_extents(text).x_advance


def font_height():
    ext = ctx.font_extents()
    return ext[2]


def draw_text(x, y, text):
    ctx.move_to(x, y)
    ctx.show_text(text)


def draw_center(y, text, family='Latin Modern Roman', size=10.5, slant=cairo.FONT_SLANT_NORMAL, weight=cairo.FONT_WEIGHT_NORMAL):
    set_font(family, size, slant, weight)
    w = text_width(text)
    draw_text((WIDTH - w) / 2, y, text)
    return y + font_height()


def draw_lr(y, left, right, lfont, rfont):
    set_font(*lfont)
    draw_text(LEFT, y, left)
    lh = font_height()
    set_font(*rfont)
    rw = text_width(right)
    draw_text(RIGHT - rw, y, right)
    rh = font_height()
    return y + max(lh, rh)


def wrap_lines(text, max_width):
    words = text.split()
    lines = []
    current = ''
    for word in words:
        cand = word if not current else current + ' ' + word
        if text_width(cand) <= max_width:
            current = cand
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(y, x, text, max_width, family='Latin Modern Roman', size=10.5, slant=cairo.FONT_SLANT_NORMAL, weight=cairo.FONT_WEIGHT_NORMAL, first_prefix='', later_prefix=''):
    set_font(family, size, slant, weight)
    words = text.split()
    lines = []
    current = ''
    prefix = first_prefix
    for word in words:
        cand = word if not current else current + ' ' + word
        if text_width(prefix + cand) <= max_width:
            current = cand
        else:
            lines.append(prefix + current)
            current = word
            prefix = later_prefix
    if current:
        lines.append(prefix + current)
    h = font_height()
    for line in lines:
        draw_text(x, y, line)
        y += h + LINE_GAP
    return y


def draw_bullet(y, text):
    set_font('Latin Modern Roman', 10.5, weight=cairo.FONT_WEIGHT_BOLD)
    draw_text(BULLET_X, y, '–')
    return draw_wrapped(y, TEXT_X, text, RIGHT - TEXT_X)

name_font = ('Latin Modern Roman', 24, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
contact_font = ('Latin Modern Roman', 9.5, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
section_font = ('Latin Modern Roman Caps', 11.5, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
org_font = ('Latin Modern Roman', 10.5, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
body_font = ('Latin Modern Roman', 10.0, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
italic_font = ('Latin Modern Roman', 10.0, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
project_font = ('Latin Modern Roman', 10.0, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
project_meta_font = ('Latin Modern Roman', 10.0, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)
body_bold_font = ('Latin Modern Roman', 10.0, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

y = 38
y = draw_center(y, 'Luke Peter Wilson', *name_font)
y += 6
y = draw_center(y, 'San Diego, CA | lukepeterwilson26@gmail.com | (760) 855-2996 | linkedin.com/in/luke-wilson', *contact_font)

y += 18
set_font(*section_font)
draw_text(LEFT, y, 'Education')
y += font_height() + 8

y = draw_lr(y, 'University of California, San Diego', 'San Diego, CA', org_font, body_font)
y += 4
y = draw_lr(y, 'Master of Science in Electrical Engineering', 'Sept. 2025 – Dec. 2026', italic_font, italic_font)
y += 4
y = draw_wrapped(y, TEXT_X, 'Coursework: VLSI Digital System Algorithms and Architectures; VLSI Integrated Circuits and Systems Design; Advanced Computer Architecture; Digital Signal Processing; Information Theory and Communications; Random Processes and Stochastic Modeling; and Microwave/RF Systems.', RIGHT - TEXT_X, *body_font, first_prefix='– ', later_prefix='  ')
y += 2

y = draw_lr(y, 'University of California, San Diego', 'San Diego, CA', org_font, body_font)
y += 4
y = draw_lr(y, 'Bachelor of Science in Electrical Engineering, GPA: 3.704', 'Sept. 2021 – June 2025', italic_font, italic_font)
y += 4
y = draw_wrapped(y, TEXT_X, 'Coursework: Digital Signal and Image Processing, Communication Systems, Probability Theory and Random Processes, Electromagnetism, VLSI Digital Circuits and Systems, OOP, Linear Electronic Circuits and Systems, and Linear Control Theory.', RIGHT - TEXT_X, *body_font, first_prefix='– ', later_prefix='  ')

y += 10
set_font(*section_font)
draw_text(LEFT, y, 'Technical Skills')
y += font_height() + 8
skills = [
    ('Programming:', 'Python, C/C++, Verilog, SystemVerilog, MATLAB, Bash, ARM Assembly'),
    ('EDA & Simulation:', 'ModelSim/Questa, Intel Quartus Prime, Xilinx Vivado, Synopsys Design Compiler, Cadence Virtuoso, Cadence Innovus'),
    ('Digital Design & Verification:', 'RTL design, testbenches, functional verification, gate-level simulation, synthesis, static timing analysis, CDC basics, UVM basics'),
    ('DSP & Hardware:', 'OFDM, MIMO, channel estimation, beamforming, mmWave systems, GNU Radio, Linux, USRP B210/X410, PlutoSDR'),
]
for label, text in skills:
    set_font(*body_bold_font)
    draw_text(LEFT, y, label)
    start_x = LEFT + text_width(label) + 6
    y = draw_wrapped(y, start_x, text, RIGHT - start_x, *body_font)

set_font(*section_font)
y += 8
draw_text(LEFT, y, 'Projects')
y += font_height() + 8

projects = [
    ('Dual-Core Machine Learning Accelerator for Attention Mechanisms', '| Verilog, Innovus', '2026–Present', [
        'Designing a dual-core systolic array accelerator for attention workloads with emphasis on clean RTL hierarchy, verification, and timing-driven implementation.',
        'Implementing RTL-to-GDSII flow including synthesis, place-and-route, SRAM integration, and gate-level validation for a 1 GHz target.',
        'Debugging functional and timing issues across block interfaces, strengthening experience with hardware integration and pre-silicon validation.',
    ]),
    ('Near-Field MIMO Ground Station Testbed', '| MATLAB, Python, GNU Radio, USRP', '2025', [
        'Built a 2x2 mmWave MIMO hardware testbed to extract CSI and automate experiments with Python and Linux.',
        'Processed experimental results to analyze channel behavior and support a co-authored IEEE INFOCOM 2026 paper.',
        'Strengthened debugging skills across hardware/software interfaces by iterating between simulation, scripting, and lab measurements.',
    ]),
    ('Kogge-Stone Adder', '| Cadence Virtuoso, CMOS Logic, Dynamic Logic', '2025', [
        'Collaborated on an 8-bit adder design capable of operating above 1.8 GHz in Virtuoso.',
        'Experimented with multiple logic styles, achieving 3.1 GHz performance with an optimized implementation.',
    ]),
]
for title, meta, date, bullets in projects:
    y = draw_lr(y, title, date, project_font, body_font)
    y += 2
    set_font(*project_meta_font)
    draw_text(LEFT, y, meta)
    y += font_height() + 2
    for bullet in bullets:
        y = draw_bullet(y, bullet)
    y += 2

set_font(*section_font)
y += 4
draw_text(LEFT, y, 'Experience')
y += font_height() + 8

experience = [
    ('Research Volunteer, WCSNG @ UCSD', 'June 2024 – Present', 'University of California, San Diego', 'La Jolla, CA', [
        'Designed simulations related to wireless communications and translated them into hardware testbeds for experimental validation.',
        'Collaborated with PhD students to perform experiments, analyze results, and troubleshoot implementation issues.',
        'Participated in weekly meetings to discuss findings and critique current research papers.',
    ]),
    ('Teaching Assistant, ECE Department', 'Sept. 2025 – Dec. 2025', 'University of California, San Diego', 'La Jolla, CA', [
        'Assisted in teaching Electromagnetism, including hosting office hours and tutoring sessions.',
        'Evaluated student performance through grading homework, exams, and projects.',
    ]),
]
for role, date, org, loc, bullets in experience:
    y = draw_lr(y, role, date, org_font, body_font)
    y += 4
    y = draw_lr(y, org, loc, italic_font, italic_font)
    y += 2
    for bullet in bullets:
        y = draw_bullet(y, bullet)
    y += 2

set_font(*section_font)
y += 4
draw_text(LEFT, y, 'Extra Information')
y += font_height() + 8
set_font(*body_bold_font)
draw_text(LEFT, y, 'Highlights:')
start_x = LEFT + text_width('Highlights:') + 6
y = draw_wrapped(y, start_x, 'Booker Award recipient, 99th percentile SAT, valedictorian of high school, proficient in German.', RIGHT - start_x, *body_font)

ctx.show_page()
surface.finish()
