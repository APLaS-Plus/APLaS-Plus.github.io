---
title: 基于Hexo框架搭建个人博客记录
typora-root-url: 基于Hexo框架搭建个人博客记录
date: 2024-05-11 01:58:39
category: 
   - Techonology
tags: 
   - Hexo
   - Persional Deploy
---

## 操作

### 在GitHub上部署自己的博客 Deploy your blog on GitHub

1. 下载并安装**git**和**node.js**。

2. 在存放博客文件的目录下新建**Hexo**文件夹用于下载存放**Hexo框架**。

3. 在博客目录下打开**Git Bash**，在[Hexo官网](https://hexo.io/zh-cn/index.html)里依次输入安装指令，即可完成安装。

   ```shell
   npm install hexo-cli -g
   hexo init blog
   cd blog
   npm install
   hexo server
   ```

4. 在[官方主题网站](https://hexo.io/themes/)下载主题，参照主题里的官方文档下载对应的文件到`./blog/themes`文件夹内，每次更新可以进入对应主题文件夹内，打开Git Bash，输入`git pull`来进行更新，下载完根据官网文档，安装一些依赖库，将**Hexo**的gitalk中变量themes的值改成你想要更改的主题的名字，Git Bash中输入`hexo g`更新网页，后面再启动服务就能看到更新后的主题了。除此之外，配置文件中还有很多别的变量也可以进行探索，以上在[官方文档](https://hexo.io/zh-cn/docs/)中有详细的描述。

   ![n1](n1.png )

5. 到目前为止，我们的博客都是在本地的，因此需要挂载到服务器上，才能真正成为一个别人能访问的网页博客，我选择部署在GitHub上，运用了GitHub推出的GitHub Page功能，参考[官方部署文档](https://hexo.io/zh-cn/docs/github-pages)，第一步要学怎么在GitHub建立一个库，此处为了学习git的一些知识，不打算使用官方提供的一键部署。

   > 1. 首先在自己的GitHub上开一个库名字为`你的GitHub用户名.github.io`
   >
   > 2. 然后更改你的./blog名字为库的同名字，进入blog目录打开Git Bash，输入以下指令：
   >
   >    ```shell
   >    git init
   >    git add .
   >    git commit -m "First init"
   >    git branch -M main
   >    git remote add origin 库URL（到你的库上复制下来，用来链接到库上的）
   >    git push -u origin master
   >    ```
   >
   >    输入以上指令，应该就成功上传库了，每次更新就再次输入最后一条指令就行了，你在新建库之后GitHub网页会给你提示，如下：
   >
   >    ![n2](n2.png)
   >
   > 3. 命令行输入`node -v`，查询并记下node的版本，我这里是`v20.12.0`。
   >
   > 4. 在GitHub你建立的库中选中`Settings > Pages > Source`，将其改为`GitHub Actions`。
   >
   > 5. 继续在网页端中建立`.github/workflows/pages.yml`（本人选择在本地写好后再次上传），填入以下内容并且更改版本号为本地版本号：
   >
   >    ```yaml
   >    name: Pages
   >    
   >    on:
   >      push:
   >        branches:
   >          - main  # default branch
   >    
   >    jobs:
   >      build:
   >        runs-on: ubuntu-latest
   >        steps:
   >          - uses: actions/checkout@v4
   >            with:
   >              token: ${{ secrets.GITHUB_TOKEN }}
   >              # If your repository depends on submodule, please see: https://github.com/actions/checkout
   >              submodules: recursive
   >          - name: Use Node.js 20
   >            uses: actions/setup-node@v4
   >            with:
   >              # Examples: 20, 18.19, >=16.20.2, lts/Iron, lts/Hydrogen, *, latest, current, node
   >              # Ref: https://github.com/actions/setup-node#supported-version-syntax
   >              node-version: '20'
   >          - name: Cache NPM dependencies
   >            uses: actions/cache@v4
   >            with:
   >              path: node_modules
   >              key: ${{ runner.OS }}-npm-cache
   >              restore-keys: |
   >                ${{ runner.OS }}-npm-cache
   >          - name: Install Dependencies
   >            run: npm install
   >          - name: Build
   >            run: npm run build
   >          - name: Upload Pages artifact
   >            uses: actions/upload-pages-artifact@v3
   >            with:
   >              path: ./public
   >      deploy:
   >        needs: build
   >        permissions:
   >          pages: write
   >          id-token: write
   >        environment:
   >          name: github-pages
   >          url: ${{ steps.deployment.outputs.page_url }}
   >        runs-on: ubuntu-latest
   >        steps:
   >          - name: Deploy to GitHub Pages
   >            id: deployment
   >            uses: actions/deploy-pages@v4
   >    ```
   >
   > 6. 经历以上种种，你应该已经成功部署GitHub Page了，点开自己的链接看看吧！我的是[一只帕勒斯的小站](https://aplas-plus.github.io/)。

### 图片显示 Display of the picture

我发现正常的上传md文件，其中的图片并不能正常显示，解决办法有两个，其一是在网络上上传图片，并贴上图片对应的url，其二是修改hexo的配置，使其能识别服务器上的图片，以下是我的操作过程：

> 1. 首先下载插件**hexo-renderer-marked**，他能方便我们对图片文件夹的管理：
>
>    `npm install hexo-renderer-marked`
>
> 2. 然后更改 **.config.yml** 中的`post_asset_folder`值为`true`，添加以下匹配值：
>
>    ```yaml
>    marked:
>      prependRoot: true
>      postAsset: true
>    ```
>
>    他的功能是建立新文章的时候会添加一个同名的文件夹，该文件夹将作为本文章的图片存储目录。
>
> 3. 然后修改`scaffolds`文件夹下的`post.md`，添加哈希值`typora-root-url: {{title}}`，这样我们在用typora的时候会使图片默认路径为同文件夹下的同名文件夹，这样就方便了我们使用typora来编辑我们的文章。
>
> 4. 然后我们在文章中使用`![](图片.jpg)`格式就可以显示图片了，注意！括号内是不能有空格的，这样我们就编辑好了，但是还有一点需要注意！本地启动hexo服务可能并不会显示图片，此时我们需要上传更新我们GitHub库，在GitHub Page上是能正常显示的，最好再每次上传之前先清一下本地的缓存，输入`hexo clean`清理缓存，有些主题可能不清网页显示会出问题（如果你是Gitee用户就重新上传更新Gitee库吧~）。
>
> 5. 经历以上种种，想必你已经能在自己的博客上正常的显示图片了，恭喜你！🫡

### 分类和标签 Categories and Tags

文章的分类和贴标签对于一个长期更新博客的人的一个很重要的事情，下面是贴标签过程：

1. 首先在配置文件 **_config.yaml** 文件中对`categories`值进行如下结构更改：

   ```yaml
   categories:
   	- category1
   	- category2
   ```

   增加category1和category2两个分类，增加tag的结构也是同样的。

2. 然后在你的文章中的顶部配置区写上和上面一样结构的代码，就可以实现该功能，例如我的文章分类为category1，标签有tag1和tag2：

   ```yaml
   category:
   	- category1
   tag:
   	- tag1
   	- tag2
   ```

   想要方便的话可以在`scaffolds`文件夹下的`post.md`中加入一行`category: `，就能在生成文件的时候加上这句话了。

   

### GitHub登录评论 Commit by GitHub account

能留下评论也是一个博客的重要功能，以下是使用了gitalk来实现的评论功能，由于这里比较简单，我直接贴我用的主题的[官方文档](https://redefine-docs.ohevan.com/posts/comment)了。

尝试了gitalk之后，不知道为什么不行，但是gitcus可以正常使用。



## Hexo框架常用指令

> 以下指令均可以在[官方指令](https://hexo.io/zh-cn/docs/commands)文档中找到，仅挑选出我认为比较常用的

开启服务

`hexo server`

`hexo s`

创建新博客

`hexo new "blog name"`

更新静态文件

`hexo generate`

`hexo g`



## 参考文档

[官方文档](https://hexo.io/zh-cn/docs/)

[超详细！0成本搭建个人网站！！【建议收藏】](https://www.bilibili.com/video/BV1ts4y1f7Gu/?spm_id_from=333.788.recommend_more_video.-1&vd_source=99294a2a1c5504f559670de616463ae4)

[hexo博客如何插入图片](https://zhuanlan.zhihu.com/p/265077468)
