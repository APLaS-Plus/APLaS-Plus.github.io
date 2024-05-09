# 基于Hexo框架搭建个人博客记录

## 操作流程

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

4. 在[官方主题网站](https://hexo.io/themes/)下载主题，参照主题里的官方文档下载对应的文件到`./blog/themes`文件夹内，每次更新可以进入对应主题文件夹内，打开Git Bash，输入`git pull`来进行更新，下载完根据官网文档，安装一些依赖库，将**Hexo**的配置文件**.config.yml**中变量themes的值改成你想要更改的主题的名字，Git Bash中输入`hexo g`更新网页，后面再启动服务就能看到更新后的主题了。除此之外，配置文件中还有很多别的变量也可以进行探索，以上在[官方文档](https://hexo.io/zh-cn/docs/)中有详细的描述。

   ![image-20240509213110472](..\images\image-20240509213110472.png)

   1. 到目前为止，我们的博客都是在本地的，因此需要挂载到服务器上，才能真正成为一个别人能访问的网页博客，我选择部署在GitHub上，运用了GitHub推出的GitHub Page功能，参考[官方部署文档](https://hexo.io/zh-cn/docs/github-pages)，










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