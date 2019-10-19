# 2048KeyのGA実装。
# 参考にしたサイト：https://tech.mof-mof.co.jp/blog/ga-one-max-problem.html
import re
import random
import custom_functions

from deap import base
from deap import creator
from deap import tools
from mykeras import keras_negapozi as myk

import crypt

real_key = b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

# 初期暗号器作成
cipher = crypt.AESCipher(real_key)
msg = bytes([int(random.random()*256) for i in range(32)])
msg = b"plain teatsfdfeteatsdt"
crypted_str = cipher.encrypt(str(msg))

# GAの初期セッティング
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)
toolbox = base.Toolbox()
toolbox.register("single_byte", custom_functions.random_byte)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.single_byte, 32)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# NegaPosi のモデルを用意
filename = "./DATA4train_test/labled_good_data.pickle"
cls = myk.NegaPosi(filename, None)
cls.loadmodel("newone")

data, hoge = cls.convertdata_load(msg)
print(cls.predict(data), msg)

msg = b'\x95\xa7\x82\xdc\xc3\xf6I9\xee\x8a\x16\xbd\x07!qf\xf2].\x9e\xfe)\xfai\x04\xefm\x80\\7\xea]\xe2*\xa6\xf57\xd3\x14\xd7\xe7\xdbq\x83'
data, hoge = cls.convertdata_load(msg)
print(cls.predict(data), msg)

input()


# [00-ff]*128 -> 2048key -> 復号 -> シミズの関数で評価 -> 返す
def kerasnp(Individual):
    make_key = ''.join([i[2:] for i in Individual])
    dcipher = crypt.AESCipher(make_key)
    decrypted_str = dcipher.decrypt(crypted_str)
    cdata, clabel = cls.convertdata_load(decrypted_str)
    return cls.predict(cdata),


def print_last(Individual):
    make_key = ''.join([i[2:] for i in Individual])
    dcipher = crypt.AESCipher(make_key)
    decrypted_str = dcipher.decrypt(crypted_str)
    decrypted_message = ''.join([chr(i) for i in decrypted_str])
    print('###decypted_message', decrypted_message)
    # cdata, clabel = cls.convertdata(decrypted_str)
    return decrypted_str, Individual


toolbox.register("evaluate", kerasnp)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", custom_functions.mutate_key, indpb=0.001)
toolbox.register("select", tools.selTournament, tournsize=3)


def GA():
    # 初期集団を生成する
    pop = toolbox.population(n=300)
    CXPB, MUTPB, NGEN = 0.5, 0.2, 40  # 交差確率、突然変異確率、進化計算のループ回数

    print("進化開始")

    # 初期集団の個体を評価する
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):  # zipは複数変数の同時ループ
        # 適合性をセットする
        print(type(ind), dir(ind), ind)
        break
        make_key = ind
        ind.fitness.values = fit

    print("  %i の個体を評価" % len(pop))

     # 進化計算開始
    for g in range(NGEN):
        print("-- %i 世代 --" % g)

        ##############
        # 選択
        ##############
         # 次世代の個体群を選択
        offspring = toolbox.select(pop, len(pop))
        # 個体群のクローンを生成
        offspring = list(map(toolbox.clone, offspring))

        # 選択した個体群に交差と突然変異を適応する

        ##############
        # 交叉
        ##############
        # 偶数番目と奇数番目の個体を取り出して交差
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                # 交叉された個体の適合度を削除する
                del child1.fitness.values
                del child2.fitness.values

        ##############
        # 変異
        ##############
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # 適合度が計算されていない個体を集めて適合度を計算
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            make_key = ind
            ind.fitness.values = fit

        print("  %i の個体を評価" % len(invalid_ind))

        # 次世代群をoffspringにする
        pop[:] = offspring

        # すべての個体の適合度を配列にする
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)

    print("-- 進化終了 --")

    best_ind = tools.selBest(pop, 1)[0]
    print(list(best_ind))
    print("最も優れていた個体: %s, %s" % (best_ind, best_ind.fitness.values))
    print(''.join([i[2:] for i in best_ind]))
    print(print_last(best_ind))

GA()
