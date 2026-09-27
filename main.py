from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.utils import get_color_from_hex as hx

REF_BAG_KG = 50.0
DENSITY = {"cement": 1.30, "sand": 1.55, "gravel": 1.45, "water": 1.00, "pgs": 1.60}

RECIPES = {
    "ЭКСПЕРТ 500 (ЦЕМ I 42,5Н)": {
        "color": "#e74c3c",
        "mixes": {
            "Бетон М150 (В12,5)": dict(gravel=0.0, sand=17.0, water=4.0, density=2.20, source="pack", desc="Стяжки пола, подготовительные работы"),
            "Бетон М200 (В15)": dict(gravel=14.0, sand=11.0, water=4.0, density=2.35, source="pack", desc="Фундаменты, перекрытия, дорожки"),
            "Бетон М300 (В22,5)": dict(gravel=12.0, sand=9.0, water=3.0, density=2.35, source="pack", desc="Ответственные конструкции, лестницы"),
            "Бетон М350 (В25)": dict(gravel=10.0, sand=8.0, water=3.0, density=2.35, source="calc", desc="Прочные конструкции, монолитные каркасы"),
            "Бетон М400 (В30)": dict(gravel=9.0, sand=7.0, water=2.5, density=2.40, source="calc", desc="Максимальная прочность: чаши, колонны"),
            "Раствор М100": dict(gravel=0.0, sand=18.5, water=4.5, density=2.00, source="pack", desc="Кладка кирпича, штукатурка стен"),
        }
    },
    "ПРОФИ 450 (ЦЕМ II/А-ЗО 32,5Б)": {
        "color": "#3498db",
        "mixes": {
            "Бетон М150 (В12,5)": dict(gravel=0.0, sand=16.0, water=4.0, density=2.20, source="pack", desc="Стяжки пола, подготовительные работы"),
            "Бетон М200 (В15)": dict(gravel=12.0, sand=9.0, water=4.0, density=2.35, source="pack", desc="Фундаменты, перекрытия, дорожки"),
            "Бетон М300 (В22,5)": dict(gravel=10.0, sand=8.0, water=3.0, density=2.35, source="pack", desc="Ответственные конструкции, лестницы"),
            "Бетон М350 (В25)": dict(gravel=9.0, sand=7.0, water=2.5, density=2.35, source="calc", desc="Прочные конструкции, монолитные каркасы"),
            "Бетон М400 (В30)": dict(gravel=8.0, sand=6.0, water=2.5, density=2.40, source="calc", desc="Предельная марка для этого цемента"),
            "Раствор М100": dict(gravel=0.0, sand=15.0, water=4.5, density=2.00, source="pack", desc="Кладка кирпича, штукатурка стен"),
        }
    },
}

BG = hx('#1a252f'); CARD = hx('#2c3e50'); WHITE = hx('#ecf0f1'); GRAY = hx('#95a5a6')
ORANGE = hx('#f39c12'); GREEN = hx('#2ecc71'); BLUE = hx('#3498db'); PURPLE = hx('#8e44ad')
DARK = hx('#1a252f')


def autowrap(lbl, pad=dp(20)):
    """Label сам подстраивает высоту под переносы текста"""
    lbl.size_hint_y = None
    lbl.bind(size=lambda l, s: setattr(l, 'text_size', (s[0] - pad, None)))
    lbl.bind(texture_size=lambda l, t: setattr(l, 'height', t[1] + dp(16)))
    return lbl


class Card(BoxLayout):
    """Карточка результата: крупно вёдра/литры, ниже литры и кг"""
    def __init__(self, title, value, sub, color_hex, **kw):
        super().__init__(orientation='vertical', spacing=dp(2), **kw)
        self.size_hint_y = None
        self.height = dp(104)
        color = hx(color_hex)
        with self.canvas.before:
            Color(*CARD)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
            Color(*color)
            self._ln = Line(rounded_rectangle=[self.x, self.y, self.width, self.height, dp(10)], width=dp(2))
        self.bind(pos=self._sync, size=self._sync)
        self.add_widget(Label(text=title, color=GRAY, font_size=sp(11), bold=True, size_hint_y=0.30))
        self.add_widget(Label(text=value, color=color, font_size=sp(20), bold=True, size_hint_y=0.40))
        self.add_widget(autowrap(Label(text=sub, color=GRAY, font_size=sp(10), halign='center'), dp(8)))

    def _sync(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._ln.rounded_rectangle = [self.x, self.y, self.width, self.height, dp(10)]


class BetonApp(App):
    def build(self):
        Window.clearcolor = BG
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))

        # шапка
        header = Label(text='КАЛЬКУЛЯТОР БЕТОНА И РАСТВОРА', bold=True, font_size=sp(15),
                       color=WHITE, size_hint_y=None, height=dp(46))
        with header.canvas.before:
            Color(*PURPLE)
            r = RoundedRectangle(pos=header.pos, size=header.size, radius=[dp(10)])
        header.bind(pos=lambda w, p: setattr(r, 'pos', p), size=lambda w, s: setattr(r, 'size', s))
        root.add_widget(header)

        # переключатель режима
        mode = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(10))
        self.t_std = ToggleButton(text='Расчёт стандарт', group='mode', state='down',
                                  font_size=sp(12), bold=True, color=WHITE)
        self.t_pgs = ToggleButton(text='Расчёт для ПЩС', group='mode',
                                  font_size=sp(12), bold=True, color=WHITE)
        for t in (self.t_std, self.t_pgs):
            t.bind(state=lambda *a: self.recalc())
            mode.add_widget(t)
        root.add_widget(mode)

        # прокручиваемое содержимое
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        scroll.add_widget(content)
        root.add_widget(scroll)

        # панель ввода
        panel = BoxLayout(orientation='vertical', spacing=dp(6), size_hint_y=None, padding=dp(10))
        panel.bind(minimum_height=panel.setter('height'))
        with panel.canvas.before:
            Color(*CARD)
            pr = RoundedRectangle(pos=panel.pos, size=panel.size, radius=[dp(10)])
        panel.bind(pos=lambda w, p: setattr(pr, 'pos', p), size=lambda w, s: setattr(pr, 'size', s))

        self.sp_cement = Spinner(values=list(RECIPES.keys()), font_size=sp(11),
                                 bold=True, background_color=WHITE, color=DARK)
        self.sp_mix = Spinner(values=[], font_size=sp(11), bold=True,
                              background_color=WHITE, color=DARK)
        self.ti_vol = TextInput(text='50', input_filter='float', multiline=False,
                                font_size=sp(13), bold=True, halign='center')
        self.ti_bucket = TextInput(text='10', input_filter='float', multiline=False,
                                   font_size=sp(13), bold=True, halign='center')

        def row(text, widget):
            b = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
            l = Label(text=text, font_size=sp(12), color=WHITE, bold=True, halign='left', valign='middle')
            l.size_hint_x = 0.55
            l.bind(size=lambda lbl, s: setattr(lbl, 'text_size', (s[0], s[1])))
            b.add_widget(l)
            widget.size_hint_x = 0.45
            b.add_widget(widget)
            panel.add_widget(b)

        row('Марка цемента:', self.sp_cement)
        row('Тип смеси:', self.sp_mix)
        row('Объём смеси, л:', self.ti_vol)
        row('Объём ведра, л:', self.ti_bucket)
        self.desc_lbl = autowrap(Label(text='', color=ORANGE, font_size=sp(10), halign='left'))
        panel.add_widget(self.desc_lbl)
        content.add_widget(panel)

        # блок результатов
        self.results = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None)
        self.results.bind(minimum_height=self.results.setter('height'))
        self.cards_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(104))
        self.total_holder = BoxLayout(size_hint_y=None, height=dp(104))
        self.info_lbl = autowrap(Label(text='', color=WHITE, font_size=sp(10), halign='left'))
        with self.info_lbl.canvas.before:
            Color(*CARD)
            ir = RoundedRectangle(pos=self.info_lbl.pos, size=self.info_lbl.size, radius=[dp(10)])
        self.info_lbl.bind(pos=lambda w, p: setattr(ir, 'pos', p),
                           size=lambda w, s: setattr(ir, 'size', s))
        self.results.add_widget(self.cards_grid)
        self.results.add_widget(self.total_holder)
        self.results.add_widget(self.info_lbl)
        content.add_widget(self.results)

        # события
        self.sp_cement.bind(text=self.on_cement)
        self.sp_mix.bind(text=lambda *a: self.recalc())
        self.ti_vol.bind(text=lambda *a: self.recalc())
        self.ti_bucket.bind(text=lambda *a: self.recalc())
        self.on_cement(None, self.sp_cement.text)
        return root

    def on_cement(self, inst, text):
        mixes = list(RECIPES.get(text, {}).get('mixes', {}).keys())
        if not mixes:
            return
        self.sp_mix.values = mixes
        self.sp_mix.text = mixes[0]
        self.recalc()

    def recalc(self, *args):
        mix = RECIPES.get(self.sp_cement.text, {}).get('mixes', {}).get(self.sp_mix.text)
        if not mix:
            return
        try:
            bucket = float(self.ti_bucket.text.replace(',', '.'))
            target = float(self.ti_vol.text.replace(',', '.'))
        except ValueError:
            return
        if bucket <= 0 or target <= 0:
            return

        use_pgs = self.t_pgs.state == 'down'
        has_gravel = mix['gravel'] > 0
        pgs_mode = use_pgs and has_gravel

        sand_l = mix['sand'] * bucket
        gravel_l = mix['gravel'] * bucket
        water_l = mix['water'] * bucket
        mass_per_bag = (REF_BAG_KG + sand_l * DENSITY['sand']
                        + gravel_l * DENSITY['gravel'] + water_l * DENSITY['water'])
        output_per_bag = mass_per_bag / mix['density']
        scale = target / output_per_bag

        cement_kg = REF_BAG_KG * scale
        cement_l = cement_kg / DENSITY['cement']
        cement_b = cement_l / bucket
        sand_b = mix['sand'] * scale
        gravel_b = mix['gravel'] * scale
        water_b = mix['water'] * scale
        sand_kg = sand_b * bucket * DENSITY['sand']
        gravel_kg = gravel_b * bucket * DENSITY['gravel']
        water_need = water_b * bucket
        total_mass = mass_per_bag * scale

        if has_gravel:
            pgs_kg = sand_kg + gravel_kg
            pgs_l = pgs_kg / DENSITY['pgs']
            pgs_b = pgs_l / bucket
            sand_pct = 100.0 * sand_kg / pgs_kg
            gravel_pct = 100.0 - sand_pct

        src = 'рецепт с упаковки' if mix['source'] == 'pack' else 'пропорция расчётная'
        self.desc_lbl.text = f"Назначение: {mix['desc']}. Источник: {src}."

        color = RECIPES[self.sp_cement.text]['color']
        cards = [Card('ЦЕМЕНТ', f'{cement_b:.1f} вед.',
                      f'≈ {cement_l:.0f} л · {cement_kg:.1f} кг\n= {scale:.2f} мешка (50 кг)', color)]
        if pgs_mode:
            cards.append(Card('ПЩС (замена песка+щебня)', f'{pgs_b:.1f} вед.',
                              f'≈ {pgs_l:.0f} л · ≈ {pgs_kg:.0f} кг\nпесок {sand_pct:.0f}% / щебень {gravel_pct:.0f}%',
                              '#16a085'))
        else:
            cards.append(Card('ПЕСОК', f'{sand_b:.1f} вед.',
                              f'≈ {sand_b * bucket:.0f} л · ≈ {sand_kg:.0f} кг', '#f39c12'))
            if has_gravel:
                cards.append(Card('ЩЕБЕНЬ', f'{gravel_b:.1f} вед.',
                                  f'≈ {gravel_b * bucket:.0f} л · ≈ {gravel_kg:.0f} кг', '#e67e22'))
        cards.append(Card('ВОДА', f'{water_b:.1f} вед.',
                          f'≈ {water_need:.1f} л · ≈ {water_need:.0f} кг', '#3498db'))

        self.cards_grid.clear_widgets()
        for c in cards:
            self.cards_grid.add_widget(c)
        rows = (len(cards) + 1) // 2
        self.cards_grid.height = rows * dp(104) + (rows - 1) * dp(8)

        self.total_holder.clear_widgets()
        self.total_holder.add_widget(
            Card('ГОТОВАЯ СМЕСЬ', f'{target:g} л',
                 f'≈ {target / bucket:.1f} вед. · {target / 1000:.3f} м³\nмасса ≈ {total_mass:.0f} кг', '#2ecc71'))

        gravel_txt = f"щебень {mix['gravel']:g} вед., " if has_gravel else ""
        lines = [f"Базовый рецепт на 50 кг цемента (ведро {bucket:g} л): песок {mix['sand']:g} вед., {gravel_txt}вода {mix['water']:g} вед.",
                 f"Выход с 50 кг ≈ {output_per_bag:.0f} л (плотность {mix['density'] * 1000:.0f} кг/м³); нужно {cement_kg:.0f} кг цемента ({scale:.2f} мешка по 50 кг)."]
        if pgs_mode:
            lines.append(f"Режим ПЩС: {pgs_b:.1f} вед. (≈{pgs_kg:.0f} кг) заменяют песок и щебень. Идеальный состав ПЩС: песок ≈{sand_pct:.0f}% / щебень ≈{gravel_pct:.0f}%.")
        elif use_pgs and not has_gravel:
            lines.append("В этой смеси нет щебня — ПЩС не применяется, расчёт по стандарту.")
        self.info_lbl.text = "\n".join(lines)


if __name__ == '__main__':
    BetonApp().run()