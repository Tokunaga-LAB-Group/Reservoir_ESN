#!/usr/bin/env python
# -*- coding: utf-8 -*-

#################################################################
# 田中，中根，廣瀬（著）「リザバーコンピューティング」（森北出版）
# 本ソースコードの著作権は著者（田中）にあります．
# 無断転載や二次配布等はご遠慮ください．
#
# edge_of_chaos.py: 本書の図3.10に対応するサンプルコード
#################################################################

# なんかいろいろテスト用

import sys
import pathlib
# 実行ファイルのあるディレクトリの絶対パスを取得
current_dir = pathlib.Path(__file__).resolve().parent
# モジュールのあるパスを追加
sys.path.append( str(current_dir) + "/../" )
# import numpy as np
import cupy as cp
import matplotlib.pyplot as plt
from tqdm import tqdm
from models.model3 import InputLayer, ReservoirLayer, OutputLayer, ESN, Tikhonov, ParallelReservoirLayer, SerialReservoirLayer, BothReservoirLayer


if __name__ == '__main__':

    # 時系列入力データ生成
    T = 2000  # 長さ
    period = 50  # 周期
    time = cp.arange(T)
    u = cp.sin(2*cp.pi*time/period)  # 正弦波信号
    
    # スペクトル半径rhoの値を変えながらループ
    p_all = cp.empty((0, 101))
    rho_list = cp.arange(0.0, 4.0, 0.02)
    for rho in tqdm(rho_list):

        #### layer
        nodeNum = 100

        # # 入力層とリザバーを生成
        # N_x = 100  # リザバーのノード数
        # input = Input(N_u=1, N_x=N_x, input_scale=1.0, seed=0)

        # Input
        inputLayer = InputLayer(1, nodeNum, inputScale=1.0)


        # reservoir = Reservoir(N_x=N_x, density=0.05, rho = rho,
        #                       activation_func=cp.tanh, leaking_rate=1.0, seed=0)

        # Reservoir
        reservoirLayer = ReservoirLayer(nodeNum, nodeNum, nodeNum, 0.24, rho, cp.tanh, 1.0)

        # resInput1 = InputLayer(16, 32, inputScale=1, seed=11)
        # resRes1 = ReservoirLayer(32, 48, nodeNum, 0.2, rho, cp.tanh, 0.22, seed=101)

        # resInput2 = InputLayer(16, 16, inputScale=1, seed=12)
        # resRes2 = ReservoirLayer(16, 16, nodeNum, 0.3, rho, cp.tanh, 0.22, seed=102)

        # resInput3 = InputLayer(16, 16, inputScale=1, seed=13)
        # resRes3 = ReservoirLayer(16, 64, nodeNum, 0.3, rho, cp.tanh, 0.22, seed=103)

        # reservoirLayer = ParallelReservoirLayer(16, 64, [(resInput1, resRes1), (resInput2, resRes2)])
        # reservoirLayer = SerialReservoirLayer(16, 64, [resRes2, resRes3], 1)
        # reservoirLayer = BothReservoirLayer(16, 64, [(resInput1, resRes1), (resInput2, resRes2)], 1)


        # リザバー状態の時間発展
        U = u[:T].reshape(-1, 1)
        x_all = cp.empty((0, reservoirLayer.outputDimention))
        for t in range(T):
            x_in = inputLayer(U[t])
            x = reservoirLayer(x_in)
            x_all = cp.vstack((x_all, x))

        # 1周期おきの状態
        T_trans = 1000  # 過渡期
        p = cp.hstack((rho*cp.ones((int((T-T_trans)/period), 1)), 
                       x_all[T_trans:T:period, 0:100]))
        p_all = cp.vstack((p_all, p))


    p_all = p_all.get()

    # グラフ表示
    plt.rcParams['font.size'] = 12
    fig = plt.figure(figsize = (7, 7))
    plt.subplots_adjust(hspace=0.3)

    ax1 = fig.add_subplot(3, 1, 1)
    ax1.text(-0.15, 1, '(a)', transform=ax1.transAxes)
    plt.scatter(p_all[:,0], p_all[:,1], color='k', marker='o', s=5)
    plt.ylabel('p_1')
    plt.grid(True)

    ax2 = fig.add_subplot(3, 1, 2)
    ax2.text(-0.15, 1, '(b)', transform=ax2.transAxes)
    plt.scatter(p_all[:,0], p_all[:,2], color='k', marker='o', s=5)
    plt.ylabel('p_2')
    plt.grid(True)

    ax3 = fig.add_subplot(3, 1, 3)
    ax3.text(-0.15, 1, '(c)', transform=ax3.transAxes)
    plt.scatter(p_all[:,0], p_all[:,3], color='k', marker='o', s=5)
    plt.xlabel(r'$\rho$')
    plt.ylabel('p_3')
    plt.grid(True)

    # 生成するファイル名
    fname = "../output/20240716/edge_of_chaos_12.png"
    # 保存
    plt.savefig(fname, bbox_inches="tight", pad_inches=0.05, dpi=400)
