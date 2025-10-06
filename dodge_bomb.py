import os
import random
import sys
import time
import pygame as pg

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#演習課題

def gameover(screen: pg.Surface):
    # 画面を黒くするSurfaceを作成し、透明度を設定
    bg_img = pg.Surface((screen.get_width(), screen.get_height()))
    pg.draw.rect(bg_img, (0, 0, 0), bg_img.get_rect())
    bg_img.set_alpha(128)

    #画像を描画
    screen.blit(bg_img, (0, 0))
    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rect = txt.get_rect(center=(screen.get_width()/2, screen.get_height()/2 - 50))
    screen.blit(txt, txt_rect)

    # 悲しむこうかとん画像
    sad_kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 2.0)
    sad_kk_rct = sad_kk_img.get_rect(center=(WIDTH/2, HEIGHT/2 + 100))
    screen.blit(sad_kk_img, sad_kk_rct)
    
    pg.display.update()
    time.sleep(5)  # 5秒待機

def init_bb_imgs():
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_imgs.append(bb_img)
    # 加速度のリスト
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs

def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or ばくだんRect
    戻り値：判定結果タプル（横方向，縦方向）
    画面内ならTrue／画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横方向にはみ出ていたら
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: # 縦方向にはみ出ていたら
        tate = False
    return yoko, tate

def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルに対応するこうかとんの画像を格納した辞書を返す
    """
    # 向きの基準となる画像をロード
    kk_base_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_flipped_img = pg.transform.flip(kk_base_img, True, False) # 左右反転

    kk_imgs = {
        (0, 0): kk_base_img,  # 静止
        (5, 0): kk_flipped_img,  # 右
        (5, -5): pg.transform.rotozoom(kk_flipped_img, 45, 1.0),  # 右上
        (0, -5): pg.transform.rotozoom(kk_flipped_img, 90, 1.0),  # 上
        (-5, -5): pg.transform.rotozoom(kk_base_img, -45, 1.0), # 左上
        (-5, 0): kk_base_img,  # 左
        (-5, 5): pg.transform.rotozoom(kk_base_img, 45, 1.0),  # 左下
        (0, 5): pg.transform.rotozoom(kk_flipped_img, -90, 1.0), # 下
        (5, 5): pg.transform.rotozoom(kk_flipped_img, -45, 1.0), # 右下
    }
    return kk_imgs

#メイン処理
def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bb_imgs, bb_accs = init_bb_imgs()
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))  # 爆弾用の空Surface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 赤い爆弾円
    bb_img.set_colorkey((0, 0, 0))  # 四隅の黒い部分を透過
    bb_rct = bb_img.get_rect()  # 爆弾Rect
    bb_rct.centerx = random.randint(0, WIDTH)  # 爆弾横座標
    bb_rct.centery = random.randint(0, HEIGHT)  # 爆弾縦座標
    vx, vy = +5, +5  # 爆弾の速度
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 
        #衝突判定
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return  # ゲームオーバー

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
            #if key_lst[pg.K_DOWN]:
            #    sum_mv[1] += 5
            #if key_lst[pg.K_LEFT]:
            #   sum_mv[0] -= 5
            #if key_lst[pg.K_RIGHT]:
            #    sum_mv[0] += 5
        kk_img = kk_imgs[tuple(sum_mv)]
        kk_rct.move_ip(sum_mv)

        #バウンド
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        #爆弾の拡大と加速
        index = min(tmr // 500, 9)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        #画面に描画
        bb_img = bb_imgs[index]
        bb_rct = bb_img.get_rect(center=bb_rct.center) # サイズ変更に合わせてRectを更新
        avx = vx * (bb_accs[index] )
        avy = vy * (bb_accs[index] )
        bb_rct.move_ip(avx, avy)
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()