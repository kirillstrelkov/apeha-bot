
class PlayerInfo(object):
    def __init__(self, name, level, clan, hp, mana, astral, rating, astral_level):
        self.name = name
        self.level = level
        self.clan = clan
        self.hp = hp
        self.mana = mana
        self.astral = astral
        self.rating = rating
        self.astral_level = astral_level
    
    def __str__(self):
        return ", ".join([self.name, self.rating, self.hp, self.mana, self.astral, self.clan])
