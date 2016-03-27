# encoding=utf8

from wx._windows import Frame
from wx._core import App, BoxSizer, VERTICAL, HORIZONTAL,\
    CB_READONLY, EXPAND, EVT_COMBOBOX
from wx._controls import ComboBox
from src.apeha.market.stone import MarketStone
from src.apeha.market.price import Price
from wx.grid import Grid
from src.apeha.utils import unicode_str

class StoneViewer(Frame):
    __TITLE = u"Информация о камнях в кузницах"
    __SIZE = (500, 400)
    def __init__(self, parent, stones):
        Frame.__init__(self, parent, size=self.__SIZE, title=self.__TITLE)
        
        self.__stones = stones
        bozer = BoxSizer(VERTICAL)
        self.SetSizer(bozer)
        
        self.create_ui()
        
    def create_ui(self):
        main_sizer = self.GetSizer()
        
        sizer = BoxSizer(HORIZONTAL)
        
        self.cb_mod = ComboBox(self, style=CB_READONLY)
        self.Bind(EVT_COMBOBOX, self.on_cb_select_mod, self.cb_mod)
        sizer.Add(self.cb_mod, 1)
        mods = self.__stones.keys()
        for mod in mods:
            self.cb_mod.Append(mod)
        self.cb_mod.Select(0)
        
        self.cb_stone = ComboBox(self, style=CB_READONLY)
        self.Bind(EVT_COMBOBOX, self.on_cb_select_stone, self.cb_stone)
        sizer.Add(self.cb_stone, 2)
        
        main_sizer.Add(sizer, 0, EXPAND)
        
        self.list = Grid(self)
        self.list.CreateGrid(0, 2)
        self.list.SetColLabelValue(0, u"Цена")
        self.list.SetColSize(0, 150)
        self.list.SetColLabelValue(1, u"Владелец")
        self.list.SetColSize(1, 250)
        main_sizer.Add(self.list, 1, EXPAND)
        
        self.on_cb_select_mod(None)
        self.on_cb_select_stone(None)
    
    def on_cb_select_mod(self, e):
        mod = self.cb_mod.GetValue()
        stones = self.__stones[mod].keys()
        
        self.cb_stone.Clear()
        for stone in stones:
            self.cb_stone.Append(stone)
        self.cb_stone.Select(0)
        self.on_cb_select_stone(e)
        
    def on_cb_select_stone(self, e):
        mod = self.cb_mod.GetValue()
        stone = self.cb_stone.GetValue()
        self.fill_list(mod, stone)
    
    def fill_list(self, mod, stone):
        self.list.DeleteRows(numRows=self.list.GetNumberRows())
        if mod in self.__stones.keys() and stone in self.__stones[mod].keys():
            stones = self.__stones[mod][stone]
            
            i = 0
            self.list.AppendRows(len(stones))
            for stone in stones:
                self.list.SetCellValue(i, 0, unicode_str(stone.price))
                self.list.SetCellValue(i, 1, stone.owner)
                i += 1
        
def show_stones(stones):
    app = App(False)
    frame = StoneViewer(None, stones)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    stones = {
              "7x":{u"Александрит ограненный" : [MarketStone(u"наме", u"мод", Price(30.00), u"владелец")],
                    u"граненный" : [MarketStone(u"наме1", u"мод1", Price(30.00, 6.0), u"владелец1"), MarketStone(u"наме2", u"мод2", Price(30.00, 0.0), u"владелец2")]
                    },
              "5x":{u"Алек" : [MarketStone(u"наме",u"мод", Price(30.00, 5.0), u"владелец")]}
              }
    
    show_stones(stones)