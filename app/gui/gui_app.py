#!/usr/bin/env python3
import PySimpleGUI as sg
sg.theme('DarkGrey13')
layout = [[sg.Text('Barcode Datacenter GUI - Smart-Mode')],
          [sg.Button('Run pipeline (Smart-Mode)'), sg.Button('Exit')]]
window = sg.Window('Barcode Datacenter', layout)
while True:
    ev, _ = window.read()
    if ev in (None, 'Exit'):
        break
    if ev == 'Run pipeline (Smart-Mode)':
        sg.popup('Pipeline executed (stub)')
window.close()
