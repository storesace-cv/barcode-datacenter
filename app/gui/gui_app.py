#!/usr/bin/env python3
import PySimpleGUI as sg
sg.theme('DarkGrey13')
layout=[[sg.Text('Barcode Datacenter GUI (Smart-Mode)')],
        [sg.Button('Run pipeline (Smart-Mode)'), sg.Button('Exit')]]
win=sg.Window('Barcode Datacenter',layout)
while True:
    ev,_=win.read()
    if ev in (None,'Exit'):break
    if ev=='Run pipeline (Smart-Mode)':
        sg.popup('Pipeline executed (stub Smart-Mode)')
win.close()
