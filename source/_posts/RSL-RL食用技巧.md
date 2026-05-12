---
title: RSL-RL食用技巧
typora-root-url: RSL-RL食用技巧
mathjax: true
date: 2026-05-12 09:53:40
category:
tags:
---


## 前言

本文只作为我在使用rsl_rl的过程中的技巧记录，不作为零基础教程（其实也是isaacgym训练技巧了，写着写着发现只写rsl_rl不能完全涵盖我要写的内容），并且非常偏向四足机器人训练

## 环境版本

python==3.8

pytorch>=2.0.0

rsl_rl==1.0.2

> 这里不直接用较新的 `rsl_rl`，主要是因为很多学术仓库目前仍然基于 Isaac Gym；而较新的 `rsl_rl` 已经更多转向 Isaac Lab。如果你使用的是更高版本的 `rsl_rl`，本文的大部分思路仍然可以参考。

## 调参目的

首先我们明确下调参的目的，最需要避免的是炫技：

1. 提高训练速度
2. 提高训练质量

## 速度指标分析

rsl_rl默认会记录三个很重要的用来分析运行速度的指标，`Perf/collection time`、`Perf/learning_time`、`Perf/total_fps`，有些开源仓库会自己加上总共的训练时间 `iteration_time`。这三个指标里最重要的是前两个：第一个是运行仿真环境、收集这一轮训练数据所需要的时间，第二个是训练模型所需要的时间。<u>这是两个最耗时的大环节，降低这两部分的耗时，就能很大程度加快训练</u>。代码位置如下：

```python
# runners/on_policy_runner.py/OnPolicyRunner
def learn(self, num_learning_iterations, init_at_random_ep_len=False):
    ... # 一些初始化
    for it in range(self.current_learning_iteration, tot_iter):
        start = time.time()
        # Rollout
        with torch.inference_mode():
            ...
            stop = time.time()
            collection_time = stop - start # 这里更新了collection_time

            # Learning step
            start = stop
            self.alg.compute_returns(critic_obs)
            
        mean_value_loss, mean_surrogate_loss = self.alg.update()
        stop = time.time()
        learn_time = stop - start # 这里更新了learn_time
        # 这里保存一次log
        if self.log_dir is not None:
            self.log(locals())
        # 这里保存模型
        if it % self.save_interval == 0:
            self.save(os.path.join(self.log_dir, 'model_{}.pt'.format(it)))
        ep_infos.clear()
        ...
```

拿我的一些训练结果为例：

![image-20260508150233200](image-20260508150233200-17782237580801.png)

明显仿真的所需时间是比模型更新所需的时间更长，那么就可以着手仿真的优化，优化的点一般是查某些计算存在重复，重点排查奖励函数，很多开发者为了节省时间会采取最简单的实现方式，往往就会带来重复计算。如果是模型更新的时间需要优化，一般可以看看有没有“GPU不友好计算”的情况存在，即大规模从内存读写数据到显存进行计算和一些碎片化计算，这些会导致显卡利用率不高

## 参数技巧

### Robot.terrain

#### Num_cols

这个值是影响最终生成的地形的种类的，如果地形并不是那种纯随机因素的地形，完全可以将其设置成分母的公倍数，比如说如下的配比就是正确的：

```python
 terrain_proportions = [0.1, 0.1, 0.35, 0.25, 0.2]
 num_cols = 20 #20刚好是上面的数的分母的公倍数，因此能刚好和上面的小数相乘变成整数
```

因为其他条件一致的条件下，开更多列地形并不能带来更加多样性的地形，还会占用更多显存，省下来的显存就可以开更多的env，解释如下：

在isaacgym文档中[此处](https://docs.robotsfan.com/isaacgym/programming/terrain.html)是这样描述的：

> In addition to the API provided for adding flat ground planes into simulation environments, we also provide APIs and utilities for generating uneven terrains. Terrains can be added as static triangle meshes using `gym.add_triangle_mesh()`. We provide utilities to generate some simple terrains in `isaacgym/terrain_utils.py`. 

三角面（trimesh）是最常见的创建地形所用的建模方式，创建三角面地形产生的是静态几何数据，不是动态几何数据，也就是说它并不增加动态刚体数量。

在经典论文[Learning to Walk in Minutes Using Massively Parallel Deep Reinforcement Learning](https://ar5iv.labs.arxiv.org/html/2109.11978)中的A.1.2小结是这样描述的：

> #### A.1.2Contact Handling
>
> **A large part of the simulator’s computational time is spent on contact detection and handling.** Reducing the number of potential contact pairs increases simulation throughput. We optimize the model of the robot to keep only the necessary collision bodies: feet, shanks, knees, and the base.
>
> The resolution of the terrain plays an important role in contact optimization. A height field is a very common type of terrain representation, in which heights are defined on a uniform grid. However one of its unfortunate properties is that it is impossible to get vertical surfaces. In order to get a steep slope approximating a vertical step, we need high resolution, which degrades the simulation performance. Instead, we convert a low-resolution height field to a triangle mesh and correct the vertical surfaces.
>
> **Finally, in PhysX (Isaac Gym’s physics engine), even though contacts between the different robots are ignored, they are still detected.** As such, the placement of robots in the terrain influences the computational load. Spreading the robots further apart from each other is highly beneficial. In the curriculum presented here, we need to place many robots close together at the beginning of training, but they quickly disperse as the training progresses. Additionally, once the robots learn to avoid crashes, there are fewer contacts with the base and knees and fewer costly resets. We see a factor of two difference in simulation time between the first minutes and the end of the training.

大部分的计算时间是被用在了检测碰撞（Contact Detection）和碰撞响应（Contact Handling），这里还说到PhysX会忽略机器人之间的碰撞，但仍然会被检测到，这里是因为发生了检测碰撞的行为，但是不会做出碰撞响应，根据我的实践来看，我平时会在同一个地图开4096个env，尽量降低num_cols的时候，计算速度基本没差别，但是显存会有一定程度的下降，从20下降到6的时候显存直接下降了差不多1Gb

### Alg.policy

这里讲的是对于模型设计的设置

#### 肯定有用和可能无用的 Normalize

此处放一个速记表：

| 类型           | 推荐使用 |
| -------------- | -------- |
| LayerNorm      | ✅        |
| RMSNorm        | ✅        |
| BatchNorm      | ❌        |
| RunningMeanStd | ❌        |

##### 有用的

模型层里常见的这几类 Normalize，大体都在做输入尺度调整；其中有些方法还会额外学习平移项。对 RL 来说，关键区别通常不是“能不能归一化”，而是归一化时会不会依赖同 batch 里的其他样本。

* LayerNorm

​	公式为$y = \frac{x - \mathrm{E}[x]}{ \sqrt{\mathrm{Var}[x] + \epsilon}} * \gamma + \beta$。更准确地说，LayerNorm 是按单个样本的特征维做归一化，不依赖同一个 mini-batch 里的其他样本；这也是它比 BatchNorm 更适合 RL 的核心原因之一。

​	这个是最基础的Norm方式之一，对输入做完正则化之后再缩放、平移到适合模型训练的分布，比较通用，写的时候找了半天没有找到特别多的实验支持我的结论，这篇实验做了LayerNorm的消融实验：[One Policy to Run Them All: an End-to-end Learning Approach to Multi-Embodiment Locomotion](https://www.ias.informatik.tu-darmstadt.de/uploads/Team/NicoBohlinger/one_policy_to_run_them_all.pdf)，这篇论文在16种机器人上做了实验，他们的模型去掉LayerNorm之后训练速度明显变慢并且上限变差，结合我个人的经验，LayerNorm能平衡掉一些数值范围的问题，减轻模型的训练负担，从而让模型专注于训练目标，不过这个说明并不是特别学术就是了

![LayerNorm消融实验图1](x9.png)

![LayerNorm消融实验图2](x10.png)

* RMSNorm

​	公式为$y_i = \frac{x_i}{\mathrm{RMS}(x)} * \gamma_i, \quad \text{where} \quad \text{RMS}(x) = \sqrt{\epsilon + \frac{1}{n} \sum _{i=1}^{n} x_i^2}$，这个函数对比LayerNorm来说计算更加简单，RMS（Root Mean Square）均方根和方差的等价公式为$RMS(x)=\sqrt{Var(x)+Mean^2(x)+\varepsilon}$，根据RMSNorm原始论文[Root Mean Square Layer Normalization](https://arxiv.org/pdf/1910.07467)的测试结果，RMSNorm的性能和LayerNorm相当并且运行时间降低了7%~64%，对于训练和推理速度都是很大的提升

> Extensive experiments on several tasks using diverse network architectures show that RMSNorm achieves comparable performance
> against LayerNorm but reduces the running time by 7%∼64% on different models.

​	使用这个函数的假设是下一层的模型输入关注小尺度的模型输入而不关注输入的平移分布

##### 可能无用

这里的可能无用需要分情况讨论

* BatchNorm

​	公式和LayerNorm一致，根据[pytorch文档中BatchNorm的描述](https://docs.pytorch.org/docs/2.11/generated/torch.nn.BatchNorm1d.html#batchnorm1d)：

> The mean and standard-deviation are calculated per-dimension over the mini-batches and γ*γ* and β*β* are learnable parameter vectors of size C (where C is the number of features or channels of the input). By default, the elements of γ*γ* are set to 1 and the elements of β*β* are set to 0. At train time in the forward pass, the variance is calculated via the biased estimator, equivalent to `torch.var(input, correction=0)`. However, the value stored in the moving average of the variance is calculated via the unbiased estimator, equivalent to `torch.var(input, correction=1)`.
>
> Also by default, during training this layer keeps running estimates of its computed mean and variance, which are then used for normalization during evaluation. The running estimates are kept with a default `momentum` of 0.1.

​	该函数的输出依赖于和自身输入同batch的其他数据，在RL中，会经常使用旧模型输出作为baseline来更新新模型，比如PPO中计算ratio和advantage的时候，就会用到旧策略输出的action和value，和新数据相比，这些旧数据在多变的RL环境交互中大概率在数据分布上完全不相似，这让BatchNorm在训练中统计的数据变得非常不可靠。笔者个人建议不要用，适用范围很窄

* RunningMeanStd

​	功能有点像放在第一层的 BatchNorm，负责在输入模型之前先把观测做缩放和平移。比较新的 rsl_rl 已经加入了这个设置，只要在 config 的 policy 处设置 module 的 `obs_normalization=True` 就可以使用，旧版并没有这个功能。直接看新版的 rsl_rl 是怎么写这部分内容的：

```python
# rsl_rl/modules/normalization.py
class EmpiricalNormalization(nn.Module):
    """Normalize mean and variance of values based on empirical values."""

    def __init__(self, shape: int | tuple[int, ...] | list[int], eps: float = 1e-2, until: int | None = None) -> None:
        """Initialize EmpiricalNormalization module.

        .. note:: The normalization parameters are computed over the whole batch, not for each environment separately.

        Args:
            shape: Shape of input values except batch axis.
            eps: Small value for stability.
            until: If this arg is specified, the module learns input values until the sum of batch sizes exceeds it.
        """
        super().__init__()
        self.eps = eps
        self.until = until
        self.register_buffer("_mean", torch.zeros(shape).unsqueeze(0))
        self.register_buffer("_var", torch.ones(shape).unsqueeze(0))
        self.register_buffer("_std", torch.ones(shape).unsqueeze(0))
        self.register_buffer("count", torch.tensor(0, dtype=torch.long))

    @property
    def mean(self) -> torch.Tensor:
        """Return the current running mean."""
        return self._mean.squeeze(0).clone()  # type: ignore

    @property
    def std(self) -> torch.Tensor:
        """Return the current running standard deviation."""
        return self._std.squeeze(0).clone()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Normalize mean and variance of values based on empirical values."""
        return (x - self._mean) / (self._std + self.eps)

    @torch.jit.unused
    def update(self, x: torch.Tensor) -> None:
        """Learn input values without computing the output values of them."""
        if not self.training:
            return
        if self.until is not None and self.count >= self.until:
            return

        count_x = x.shape[0]
        self.count += count_x
        rate = count_x / self.count
        var_x = torch.var(x, dim=0, unbiased=False, keepdim=True)
        mean_x = torch.mean(x, dim=0, keepdim=True)
        delta_mean = mean_x - self._mean
        self._mean += rate * delta_mean
        self._var += rate * (var_x - self._var + delta_mean * (mean_x - self._mean))
        self._std = torch.sqrt(self._var)

    @torch.jit.unused
    def inverse(self, y: torch.Tensor) -> torch.Tensor:
        """De-normalize values based on empirical values."""
        return y * (self._std + self.eps) + self._mean
```

​	根据我的实际使用来看，在不少 RL 任务里直接加这个设置都会有效，能用更少的轮次训练出更好的结果。但我翻了差不多 10 个比较有影响力的四足机器人开源仓库，发现它们基本都没有尝试在实验中加入这个设置。那么大家都不约而同地不使用这个设置，我推测的理由如下：

1. 首先是一般机器人仓库中都会测量好机器的电机阻尼、电机力矩、重量、关节位置等物理属性，知道他们的范围，可以求出一个真实的scale，将obs缩放到合适的位置，这里就已经取代了一部分RunningMeanStd的作用了，没有RunningMeanStd，我反而训练、推理的更快，效果并不会差很多
2. RunningMeanStd中统计来源为仿真器，众所周知sim2real一直以来都是一个很难解决的问题，其中一个原因就是仿真器和现实的gap，因此RunningMeanStd中统计的分布一定不是真实世界的分布，也就存在不适用的可能

#### 模型层数和维度选择

如果性能不够，我更建议先尝试扩展模型层数，而不是直接增加维度。对常见的机器人 MLP 策略来说，深网络往往比宽网络更容易在相近参数预算下提升表达能力。基础一点说，一般 12 到 16 自由度的机器人，三层 256 维的线性层就已经能完成大部分任务的训练。那么当你怀疑模型表达能力不足时，为什么优先扩层而不是加宽？直观上看，扩层会叠加更多非线性变换，而单纯加宽更多是在提高同一层的拟合精度。下面这个模拟图就是用不同维度的线性函数去拟合 $y=sin(x^2)$ 的效果：

![sin_linear_fit_comparison](sin_linear_fit_comparison.png)

从这个图里可以比较直观地看到，128 维的线性函数拟合能力已经不弱了。我再借论文[On the Number of Linear Regions of Deep Neural Networks](https://proceedings.neurips.cc/paper_files/paper/2014/file/fa6f2a469cc4d61a92d96e74617c3d2a-Paper.pdf)里的结论做一个辅助说明：这篇论文讨论了以 ReLU 为激活函数的 MLP 对线性空间的切分能力。

>Theorem 5. The maximal number of linear regions of the functions computed by a neural network withn0 input units and L hidden layers, with $n_i ≥ n_0$ rectifiers at the i-th layer, is lower bounded by
>$$
>\left( \prod_{i=1}^{L-1} \left\lfloor \frac{n_i}{n_0} \right\rfloor^{n_0} \right) \sum_{j=0}^{n_0} \binom{n_L}{j}
>$$
>Corollary 6. A rectifier neural network with $n_0$ input units and L hidden layers of width $n ≥ n_0$ can compute functions that have $\Omega\left(\left(\frac{n}{n_0}\right)^{(L-1)n_0}n^{n_0}\right)$linear regions.

$\Omega()$代表了函数的渐进下界，n0是输入维度，n是每一层 hidden layer 的宽度，也就是每层 ReLU 单元数量，L是hidden layer 数量，也就是深度，第二条公式是第一条的近似解，可以看到象征模型宽度的n在指数函数的底数，象征模型深度的L在指数函数的指数，很明显同样的数值变化，L带来的影响远大于n，更深的网络有更强的切分线性空间的能力，也就是能用更小的参数增量带来更好的模型表现，即深网络比宽网络参数利用效率更高

#### 激活函数选择

先给出一个几乎所有任务都比较通用的列表：

| 名字 | 函数                                                         | 曲线                                              |
| ---- | ------------------------------------------------------------ | ------------------------------------------------- |
| elu  | $\text{ELU}(x) = \begin{cases} x, & \text{ if } x > 0\\\ \alpha * (\exp(x) - 1), & \text{ if } x \leq 0 \end{cases}$ | <img src="/ELU.png" alt="ELU 曲线" width="240">   |
| tanh | $\tanh(x) = \frac{\exp(x) - \exp(-x)} {\exp(x) + \exp(-x)}$  | <img src="/Tanh.png" alt="Tanh 曲线" width="240"> |

RL 里比较通用的激活函数，特别是用在线性层时，往往更偏向保留负半轴信息、并且激活更平滑的函数。在大部分 RL 任务里，负区间的信息都相当重要，比如角色控制需要左右、前后移动，就一定会有负区间信息；像 ReLU 这种截断型函数，通常不太适合这类低维状态输入的策略网络。这是从 obs 的数据分布来说的；如果你的输入天然几乎全是正的，比如用视觉输入训练 Atari 类任务，那么 ReLU 也可以作为一个可选项。

![Lunar Lander](lunar_lander.gif)

比较直观的可以看这个数据，来自 DeepMind 论文[What Matters In On-Policy Reinforcement Learning? A Large-Scale Empirical Study](https://arxiv.org/pdf/2006.05990#page=13.83) 的 Figure 30。左图是“按激活函数选择分组后的性能 95 分位”，右图是“进入前 5% 配置时各激活函数的分布”。从这张图里可以看出 Tanh、ELU、Sigmoid 在这组实验里表现都不错，和前面“保留负区间信息、曲线更平滑”这个经验基本一致。落到具体任务上，ELU 往往比 Tanh 更快一些，而且梯度为 0 的范围也更小；但最终还是要以实际实验为准。

![image-20260511150703827](image-20260511150703827.png)

![image-20260511150728153](image-20260511150728153.png)

### Alg.algorithm

这里讲的是对于PPO的设置

#### `desired_kl`、`schedule` 和 `learning_rate` 联调

* `learning_rate` 是训练初始学习率
* `schedule` 有两个选项，`"fixed"` 和 `"adaptive"`，前者固定学习率，后者会在训练中自动调节学习率
* `desired_kl` 一般可以理解成 target KL（目标 KL），它通常和 `schedule = "adaptive"` 联动使用

`desired_kl` 一般可以先设成任务最终收敛时 KL 散度的大约 1/3，同时把 `learning_rate` 放在 `1e-4 ~ 1e-3` 的范围，并把 `schedule` 设成 `"adaptive"`。<u>这比较适合你反复训练同一个任务、但只改了少量细节时使用，比如调整奖励函数。</u>下面会讲为什么这样设。

```python
# rsl_rl/algorithms/ppo.py
def update(self):
    ... # batch update
            # KL
            if self.desired_kl != None and self.schedule == 'adaptive':
                with torch.inference_mode():
                    kl = torch.sum(
                        torch.log(sigma_batch / old_sigma_batch + 1.e-5) + (torch.square(old_sigma_batch) + torch.square(old_mu_batch - mu_batch)) / (2.0 * torch.square(sigma_batch)) - 0.5, axis=-1)
                    kl_mean = torch.mean(kl)

                    if kl_mean > self.desired_kl * 2.0:
                        self.learning_rate = max(1e-5, self.learning_rate / 1.5)
                    elif kl_mean < self.desired_kl / 2.0 and kl_mean > 0.0:
                        self.learning_rate = min(1e-2, self.learning_rate * 1.5)
                     
                    for param_group in self.optimizer.param_groups:
                            param_group['lr'] = self.learning_rate
```

上面这一段就是更新学习率的地方。可以看到，同时开启 `desired_kl` 和 `schedule` 之后，当 $kl_{\pi} > kl_{\text{target}} \times 2$ 时，说明策略更新过猛，需要降低学习率；当 $0 < kl_{\pi} < kl_{\text{target}} / 2$ 时，说明策略更新偏保守，可以适当提升学习率。也就是说，在设置了 `schedule="adaptive"` 之后，学习率保持不变的大致区间是 $(kl_{\text{target}} / 2,\ kl_{\text{target}} \times 2)$。

工程上，我通常会先观察一次正常收敛训练里最终的 $kl_{\pi}$ 大概落在哪个量级，再把 `desired_kl` 设成这个值的约 1/3。这样做的意义是：前期允许较大的学习率加快学习，一旦 KL 偏大，学习率会自动回落；这样通常能在训练速度和最终稳定性之间取得比较实用的平衡。

#### Normalize_advantage_per_mini_batch

新版 RSL-RL 增加了 normalize_advantage_per_mini_batch 参数：False 时在整个 rollout / collected trajectories 上归一化 advantage；True 时在每个 mini-batch 内重新归一化 advantage。在1.0.2版本是写死的，只能在整个rollout上计算。代码位置如下：

```python
# rsl_rl/storage/rollout_storage.py
def compute_returns(self, last_values, gamma, lam):
    advantage = 0
    for step in reversed(range(self.num_transitions_per_env)):
        if step == self.num_transitions_per_env - 1:
            next_values = last_values
        else:
            next_values = self.values[step + 1]
        next_is_not_terminal = 1.0 - self.dones[step].float()
        delta = self.rewards[step] + next_is_not_terminal * gamma * next_values - self.values[step]
        advantage = delta + next_is_not_terminal * gamma * lam * advantage
        self.returns[step] = advantage + self.values[step]

    # Compute and normalize the advantages
    self.advantages = self.returns - self.values
    self.advantages = (self.advantages - self.advantages.mean()) / (self.advantages.std() + 1e-8) #  <--------就是这里啦
```

Normalize advantage是一个相当好用的稳定PPO训练的手段，计算简单，效果明显，根据surrogate loss的计算方式，即下面的代码：

```python
# rsl_rl/algorithms/ppo.py
# Surrogate loss
ratio = torch.exp(actions_log_prob_batch - torch.squeeze(old_actions_log_prob_batch))
surrogate = -torch.squeeze(advantages_batch) * ratio
surrogate_clipped = -torch.squeeze(advantages_batch) * torch.clamp(ratio, 1.0 - self.clip_param, 1.0 + self.clip_param)
surrogate_loss = torch.max(surrogate, surrogate_clipped).mean()
```

我们可以知道策略梯度更新依赖的一个环节是advantages_batch，通过对advantage进行归一化，可以将advantage的值修正为距离平均的advantage，原来的值表示我做的这个操作得到的得分是否好过参考值values，修正后的值表示哪些值比平均的操作更能拿分，哪些值比平均的操作更容易失分，因为经过减去`advantages.mean()`，advantage会分布在0的两侧，在训练中能更清晰表达模型的更新方向——“比平均的行为要好”；而除去`advantages.std()`则能让每一次迭代时更新的幅度都差不多，让训练保持在一个比较稳定的状态

为什么可以这样做？根据OpenAI Spinning Up里[Baselines in Policy Gradients](https://spinningup.openai.com/en/latest/spinningup/rl_intro3.html#id13)的理论：

> An immediate consequence of the EGLP lemma is that for any function $b$ which only depends on state,
>
> $$
> E_{a_t \sim \pi_{\theta}}{\nabla_{\theta} \log \pi_{\theta}(a_t|s_t) b(s_t)} = 0
> $$
> This allows us to add or subtract any number of terms like this from our expression for the policy gradient, without changing it in expectation:
>
> $$
> \nabla_{\theta} J(\pi_{\theta}) = E_{\tau \sim \pi_{\theta}}{\sum_{t=0}^{T} \nabla_{\theta} \log \pi_{\theta}(a_t |s_t) \left(\sum_{t'=t}^T R(s_{t'}, a_{t'}, s_{t'+1}) - b(s_t)\right)}
> $$
> Any function $b$ used in this way is called a **baseline**.

在期望策略梯度中，加减$b(s_t)$对期望梯度不会产生任何影响，因为$b(s_t)$ 不依赖 action，减掉它不会改变 policy gradient 的期望方向，可以把 advantages.mean() 近似看作当前 batch 的常数 baseline。由于它不直接依赖某个样本的 action，在标准 policy gradient 的期望形式下，减去 action-independent baseline 不改变期望梯度方向。但在有限 batch、sample，mean 由当前采样数据估计、并且 PPO surrogate 带 clipping 的情况下，它并不是严格“完全不影响训练结果”，而是主要改变单次更新的方差、符号分布和优化轨迹。除以 advantages.std() 本质上是对 policy loss / policy gradient 做正数缩放。它不会改变 advantage 的排序，但会改变梯度幅度；在固定 learning rate、PPO clipping、adaptive KL schedule 存在时，它会影响优化轨迹。因此它不是“不影响期望梯度”，而是把每轮 update 的有效尺度稳定到类似范围

## 其他技巧

### 预训练模型

训练要尽可能使用预训练模型，不管是第三方训练出的通用模型还是你自己训练出的一个不错的模型。理由如下：

首先假设你找到的预训练模型，已经把策略覆盖到了包含当前任务的观测-动作分布，也就是：

$$
d_{\pi_{\mathrm{tar}}}(s)\pi_{\mathrm{tar}}(a\mid s) \ll d_{\pi_{\mathrm{pre}}}(s)\pi_{\mathrm{pre}}(a\mid s)
$$

在这个前提下，使用预训练模型可以很大程度加快训练进程。特别是一些训练后期才能表现出来的特性，因为 RL 追求的是奖励最大，最容易拿到奖励的行为往往会先被学出来；而那些难拿到分数的奖励项，梯度信号通常更弱，往往要到后半程才会逐步学出来。这时候，预训练模型就能帮助你更快跳过前期训练。



## 后记

写了接近有五天，都是我工作中的工程经验，如果对读者能带来帮助，那确实是我莫大的荣幸，欢迎评论交流

![1778474160743](1778474160743.gif)
