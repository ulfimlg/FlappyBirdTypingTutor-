import pygame
import sys
def load():
    # path of player with different states
    PLAYER_PATH = (
            'assets/sprites/redbird-upflap.png',
            'assets/sprites/redbird-midflap.png',
            'assets/sprites/redbird-downflap.png'
    )

    # path of background
    BACKGROUND_PATH = 'assets/sprites/background-black.png'

    # path of pipe
    PIPE_PATH = 'assets/sprites/pipe-green.png'

    IMAGES, SOUNDS, HITMASKS, WORDS= {}, {}, {}, {}

    # numbers sprites for score display
    IMAGES['numbers'] = (
        pygame.image.load('assets/sprites/0.png').convert_alpha(),
        pygame.image.load('assets/sprites/1.png').convert_alpha(),
        pygame.image.load('assets/sprites/2.png').convert_alpha(),
        pygame.image.load('assets/sprites/3.png').convert_alpha(),
        pygame.image.load('assets/sprites/4.png').convert_alpha(),
        pygame.image.load('assets/sprites/5.png').convert_alpha(),
        pygame.image.load('assets/sprites/6.png').convert_alpha(),
        pygame.image.load('assets/sprites/7.png').convert_alpha(),
        pygame.image.load('assets/sprites/8.png').convert_alpha(),
        pygame.image.load('assets/sprites/9.png').convert_alpha()
    )

    alphabetlist=[x for x in 'abcdefghijklmnopqrstuvwxyz']
    IMAGES['alphabet'] = ({})
    IMAGES['alphabet2'] = ({})
    for i in alphabetlist:
        IMAGES['alphabet'][i]=pygame.image.load('assets/sprites/char_ext/'+i+'.png').convert_alpha()
        IMAGES['alphabet2'][i+'2']=pygame.image.load('assets/sprites/char_ext/'+i+'2.png').convert_alpha()


    WORDS= ["cursed", "anguish","frustration", "jumping","triumph", "crazed","elated", "wizard","irritate", "terrified",
            "drumroll", "dishearten", "depress", "annoying", "vexatious",
            "trying", "troubled", "unpleasant", "failing", "unhappy", "falling", "chopsticks", "thwarts",
            "disappoint", "infuriate", "jubilant", "pleasurable", "festive", "rapturous", "joyful",
            "gratified", "beaming", "radiant", "fortunate", "delighted", "gleeful", "cheerful", "chirpy",
            "optimist", "vivacious", "jaunty", "carefree", "bouncy", "quizzical", "searching", "amusing",
            "eccentric", "speaker", "mocking", "gracious", "flippant", "frivolous", "danger", "accident",
            "unhealthy", "wicked", "dynamite", "elbow", "flapping", "gliding", "carpet", "pineapple",
            "transport", "museum", "keyboard", "trigonometry", "airmail", "downtown", "encyclopedia",
            "hacksaw", "knowledge", "kettledrum"
            ]

    # base (ground) sprite
    IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

    # sounds
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

    # select random background sprites
    IMAGES['background'] = pygame.image.load(BACKGROUND_PATH).convert()

    # select random player sprites
    IMAGES['player'] = (
        pygame.image.load(PLAYER_PATH[0]).convert_alpha(),
        pygame.image.load(PLAYER_PATH[1]).convert_alpha(),
        pygame.image.load(PLAYER_PATH[2]).convert_alpha(),
    )

    # select random pipe sprites
    IMAGES['pipe'] = (
        pygame.transform.rotate(
            pygame.image.load(PIPE_PATH).convert_alpha(), 180),
        pygame.image.load(PIPE_PATH).convert_alpha(),
    )

    # hismask for pipes
    HITMASKS['pipe'] = (
        getHitmask(IMAGES['pipe'][0]),
        getHitmask(IMAGES['pipe'][1]),
    )

    # hitmask for player
    HITMASKS['player'] = (
        getHitmask(IMAGES['player'][0]),
        getHitmask(IMAGES['player'][1]),
        getHitmask(IMAGES['player'][2]),
    )
    
    return IMAGES, SOUNDS, HITMASKS, WORDS

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in range(image.get_width()):
        mask.append([])
        for y in range(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask
