from core import Face,Entity,Game,getNIndexesRandomly,ge


class Fail(Face):
    def __init__(self, owner : Entity):
        super().__init__("FAIL", owner, 0)

    def apply(self, game, target : Entity):
        ge.print("nothing happens")
        self.owner.playedThisTurn = True

    def defaultTarget(self, game):
        return self._selectNone(game)

class Attack(Face):
    def __init__(self, owner : Entity, dmg, tier):
        super().__init__("Attack"+str(dmg), owner, tier)
        self.dmg = dmg

    def apply(self, game, target : Entity):
        """target must be the one to attack"""
        if target is None:
            ge.print("No one to attack")
        else:
            target.handleAttack(self.owner.concentration*self.dmg,False)
        self.owner.playedThisTurn = True

    def defaultTarget(self, game):
        return self._selectWeakestOppWithoutTooMuchArmor(game)

class Heal(Face):
    def __init__(self, owner : Entity, heal, tier):
        super().__init__("Heal"+str(heal), owner, tier)
        self.heal = heal

    def apply(self, game, target : Entity):
        """target must be the one to heal"""
        # Target can't be None as the caster is alive
        target.handleHeal(self.owner.concentration*self.heal)
        self.owner.playedThisTurn = True

    def defaultTarget(self, game):
        return self._selectWeakestFriend(game)

class Armor(Face):
    def __init__(self, owner : Entity, armor, tier):
        super().__init__("Armor"+str(armor), owner, tier)
        self.armor = armor

    def apply(self, game, target: Entity):
        """target must be the one to armor"""
        # Target can't be None as the caster is alive
        target.activeArmor = self.owner.concentration*self.armor
        self.owner.playedThisTurn = True
        
        ge.print(f"{target.name} gains {self.owner.concentration*self.armor} armor")

    def defaultTarget(self, game):
        return self._selectSelf(game)

class Concentration(Face):
    def __init__(self, owner : Entity, tier):
        super().__init__("Concentration", owner, tier)

    def apply(self, game, target: Entity):
        """target is ignored"""
        self.owner.concentration *= 2
        ge.print(f"{self.owner.name} concentrates")
        assert target is None, "WEIRD"
        # Do not set self.owner.playedThisTurn to True
            
    def defaultTarget(self, game):
        return self._selectNone(game)

class Stun(Face):
    def __init__(self, owner : Entity, tier):
        super().__init__("Stun", owner, tier)
    
    def apply(self, game, target: Entity):
        """Target is stunned"""
        if target is None:
            ge.print("No one to stun")
        else:
            self.owner.stunning = target
            ge.print(f"{target.name} is stunned")
        self.owner.playedThisTurn = True
        

    def defaultTarget(self, game):
        return self._selectWeakestOpp(game)

class Sweep(Face):
    def __init__(self, owner: Entity, dmg, tier):
        super().__init__("Sweep"+str(dmg), owner, tier)
        self.dmg = dmg

    def apply(self, game, target: Entity):
        """Target is ignored"""
        for entity in game.entities:
            if entity.team != self.owner.team and entity.alive():
                entity.handleAttack(self.owner.concentration*self.dmg,False)
        self.owner.playedThisTurn = True

    def defaultTarget(self, game):
        return self._selectNone(game)

class Fireball(Face):
    def __init__(self, owner : Entity, dmg, tier):
        super().__init__("Fireball"+str(dmg), owner, tier)
        self.dmg = dmg

    def apply(self, game, target : Entity):
        """target must be the one to attack"""
        if target is None:
            ge.print("No one to fireball")
        else:
            target.handleAttack(self.owner.concentration*self.dmg,True)
        self.owner.playedThisTurn = True

    def defaultTarget(self, game):
        return self._selectWeakestOpp(game)

class Upgrade(Face):
    """Concentration is ignored"""
    def __init__(self, owner : Entity, tier1Stack, tier2Stack, tier3Stack):
        super().__init__("Upgrade", owner, 4)
        self.tierStack = [tier1Stack,tier2Stack,tier3Stack]

    def apply(self, game, target: Entity):
        """Target is ignored. always upgrade the weakest face"""
        weakestFaceIndex = None
        weakestFaceTier = None
        for k,v in enumerate(self.owner.faces):
            if v.tier<4 and (weakestFaceTier is None or v.tier < weakestFaceTier):
                weakestFaceIndex = k
                weakestFaceTier = v.tier

        assert weakestFaceTier is not None, "WEIRD"
        newFaceTier = min(weakestFaceTier+1, 3)

        index  = getNIndexesRandomly(self.tierStack[newFaceTier-1],1,False)[0] # minus one because of indexes
        self.owner.faces.pop(weakestFaceIndex)
        addSpellByString(self.owner,self.tierStack[newFaceTier-1][index],newFaceTier)
        self.owner.playedThisTurn = True


    def defaultTarget(self, game):
        return self._selectSelf(game)

class Tank(Face):
    def __init__(self, owner : Entity):
        super().__init__("Tank", owner, 4)
        self.armor = 4

    def apply(self, game, target: Entity):
        """Target is ignored"""
        self.owner.taunting = True
        self.owner.activeArmor = self.owner.concentration*self.armor
        ge.print(f"{target.name} gains {self.owner.concentration*self.armor} armor")
        self.owner.playedThisTurn = True

    def defaultTarget(self, game):
        return self._selectSelf(game)

class Vampire(Face):
    def __init__(self, owner):
        super().__init__("Vampire", owner, 4)

    def apply(self, game, target):
        hpLost = 0
        if target is None:
            ge.print("No one to Vampireise")
        else:
            hpLost = target.handleAttack(2*self.owner.concentration,True)
        self.owner.handleHeal(hpLost)
        self.owner.playedThisTurn = True

    def defaultTarget(self, game):
        return self._selectWeakestOpp(game)

class King(Face):
    def __init__(self, owner):
        super().__init__("King", owner, 4)
        self.dmg = 2 # Needed for _selectWeakestOppWithoutTooMuchArmor
        self.heal = 1
        self.armor = 1

    def apply(self, game, target):
        if target is None:
            ge.print("No one to attack")
        else:
            target.handleAttack(self.dmg*self.owner.concentration,False)
        self.owner.handleHeal(self.heal*self.owner.concentration)
        self.owner.activeArmor = self.armor*self.owner.concentration
        ge.print(f"{self.owner.name} gains {self.owner.concentration*self.armor} armor")
        self.owner.playedThisTurn = True

    def defaultTarget(self, game):
        return self._selectWeakestOppWithoutTooMuchArmor(game)


class Paladin(Face):
    def __init__(self, owner):
        super().__init__("Paladin", owner, 4)

    def apply(self, game, target):
        self.owner.immune = True
        self.owner.playedThisTurn = True

    def defaultTarget(self, game):
        return self._selectSelf(game)

class Lich(Face):
    def __init__(self, owner):
        super().__init__("Lich", owner, 4)

    def apply(self, game : Game, target):
        """target is ignored"""
        nbOfGhoulsToSpawn = 1*self.owner.concentration
        for k in range(nbOfGhoulsToSpawn):
            if game.canSpawnGhoul():
                ghoul = createGhoul(self.owner)
                ghoul.playedThisTurn = True # Ghoul cannot play immediatly
                ge.print("ghoul spawned")
                game.entities.append(ghoul)
            else:
                ge.print("too many ghouls")
        self.owner.playedThisTurn = True

    def defaultTarget(self, game):
        return self._selectSelf(game)
    
def createGhoul(father : Entity):
    ghoulHp = 1
    p = Entity(ghoulHp, "Ghoul", father.team, father)
    p.faces.append(Fail(p))
    p.faces.append(Fail(p))
    p.faces.append(Fail(p))
    p.faces.append(Fail(p))
    p.faces.append(Attack(p,2,1))
    p.faces.append(Attack(p,1,1))
    return p

def addSpellByString(player, string, tier):
    if string[0:3] == "Att":
        player.faces.append(Attack(player,int(string[-1]), tier))
    elif string[0:3] == "Hea":
        player.faces.append(Heal(player,int(string[-1]), tier))
    elif string[0:3] == "Swe":
        player.faces.append(Sweep(player,int(string[-1]), tier))
    elif string[0:3] == "Fir":
        player.faces.append(Fireball(player,int(string[-1]), tier))
    elif string[0:3] == "Arm":
        player.faces.append(Armor(player,int(string[-1]), tier))
    elif string[0:3] == "Con":
        player.faces.append(Concentration(player, tier))
    elif string[0:3] == "Tan":
        player.faces.append(Tank(player))
    elif string[0:3] == "Vam":
        player.faces.append(Vampire(player))
    elif string[0:3] == "Kin":
        player.faces.append(King(player))
    elif string[0:3] == "Pal":
        player.faces.append(Paladin(player))
    elif string[0:3] == "Lic":
        player.faces.append(Lich(player))
    elif string[0:3] == "Fai":
        player.faces.append(Fail(player))
    else:
        assert False, "WEIRD"