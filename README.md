# pyModbusServerGUI
运行Modbus服务器以进行测试的基本GUI，告诉它要显示什么数据，而不是将它连接到一些OT套件以进行数据馈送。它允许您设置哪些线圈响应为启用，并为输入寄存器设置值，也可以将其设置为随机值。
利用pyModbusTCP进行所有艰苦的工作：https://github.com/sourceperl/pyModbusTCP
GUI组件使用dearpygui框架：https://github.com/hoffstadt/DearPyGui
Roadmap是添加离散输入，支持更新远程客户端正在更新的值（您现在可以更新它们，但它不会反映在GUI中），然后可能允许随着时间的推移更改值。甚至可以将其发展为真正的数据馈送，几乎就像一个合适的Modbus服务器！


# 用法
要求pyModbusTCP和dearpygui安装有：
`sudo pip install dearpygui pyModbusTCP`
下载所有文件，然后运行：
`python pyModbusServerGUI-v0.2.py`
机器上应该有一个可用IP地址的下拉列表，以选择服务器将监听的地址。标准Modbus/TCP端口是502，但这需要使用root权限运行。
要设置线圈，有两个选项：
-使用线圈GUI点击将启用的线圈地址，或者只使用随机化按钮。通过将X和Y标题值加在一起，可以找到每个线圈的地址。
-键入/粘贴要启用的线圈地址的值的逗号分隔列表。
要设置输入或输出寄存器值，请将它们键入网格上的相关框中，目前我只启用了1000个值，否则表会变得巨大，您可以通过更改代码中为“NUMREGISTERS”设置的值来更改这一点。。如果需要，可以添加某种CSV导入。同样，寄存器的真实地址是通过添加X和Y标头值来找到的，例如，在屏幕截图上，值“435”将在地址30042处找到。
调试信息会被转储到控制台中，所以如果出现错误，那么在您启动它的终端中可能会有一些提示。

1.在modbus服务器上我集成了业务类型，分别是PCS（储能变流器）、BMS（电池管理系统），点击自动模拟即可每秒随机生成模拟数据，并将数据写入到modbus服务器里面，可以通过客户端远程读取和修改服务器数据。

2.在电池堆界面可以查看具体数据，和每秒数据变化曲线。

3.在PCS配置界面可根据时间顺序配置pcs事件，例如3秒时设备断开，5秒时设备重启，7秒时设置PCS电压、电流、功率数值等，设置循环执行次数，可以导入配置，导出配置。

4.操作信息可以点开右边的日志查看。

# 图片

1.主界面

![](https://github.com/600888/pyModbusServerGUI-test/blob/linux/resources/img/1.png)

2.输出线圈值界面

![](https://github.com/600888/pyModbusServerGUI-test/blob/linux/resources/img/2.png)

3.模拟输入寄存器

![](https://github.com/600888/pyModbusServerGUI-test/blob/linux/resources/img/3.png)

4.自定义PCS配置信息

![](https://github.com/600888/pyModbusServerGUI-test/blob/linux/resources/img/4.png)

5.PCS信息界面

![](https://github.com/600888/pyModbusServerGUI-test/blob/linux/resources/img/5.png)

6.电池堆信息界面

![](https://github.com/600888/pyModbusServerGUI-test/blob/linux/resources/img/6.png)

7.电池簇信息界面

![](https://github.com/600888/pyModbusServerGUI-test/blob/linux/resources/img/7.png)
