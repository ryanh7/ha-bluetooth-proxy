# Bluetooth Proxy
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

适用于home assistant的蓝牙代理集成，可通过IP网络接收ble广播信息。目前不支持蓝牙主动连接。

## 配置
home assistant配置 > 设备与服务 > 添加集成 > Bluetooth Proxy

## 端口
开放以下端口
- udp 5038

## 蓝牙网关
在包含蓝牙适配器的主机上运行相关脚本以充当蓝牙网关。主机上需提前安装以下软件包：
- python3
- python3-bleak

所需python包可通过pip3安装:
```bash
pip3 install bleak
```
准备妥当后可在主机上运行agent目录下提供的脚本：
```bash
python3 ble_agent.py -H home-assistant的IP
```
如需检查发送的ble广播信息，可添加参数-v
```bash
python3 ble_agent.py -H home-assistant的IP -v
```
脚本将通过udp协议向home assistant发送json格式的ble广播信息
