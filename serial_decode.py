import io
import time
import threading

import serial
from ui.ui import GPIODisplay

# Função para ler dados usando um mock da porta serial
def read_gpio_data(serial_port, stop_event):
    while not stop_event.is_set():
        with serial.Serial(serial_port, baudrate=9600, timeout=1, stopbits=1, ) as ser:
            while True:
                start_byte = ser.read(1)
                # print(start_byte)
                if start_byte == b'S':
                    num_active_gpios = ord(ser.read(1))  # Recebe o byte que representa a quantidade de GPIOs ativos
                    gpio_list = []
                    gpios_high = []

                    for _ in range(num_active_gpios):
                        gpio_byte = ord(ser.read(1))
                        gpio_num, gpio_in_out, gpio_high_low = decode_gpio_data(gpio_byte)
                        gpio_list.append((gpio_num, gpio_in_out, gpio_high_low))

                    end_byte = ser.read(1)
                    if end_byte == b'E':
                        for gpio in gpio_list:
                            if gpio[1] == 'out':
                                if gpio[2] == 'low':
                                    gpios_high.append(gpio[0])
                            print(f"GPIO Número: {gpio[0]}, Direção: {gpio[1]}, Estado: {gpio[2]}")
                        app.turn_gpios_high(gpios_high)
                    else:
                        print("Erro: Byte de finalização incorreto")
                else:
                    print("Erro: Byte de início incorreto")
                # Reposiciona o ponteiro do buffer para o início após leitura completa
                # ser.seek(0)
                # time.sleep(1)

# Função auxiliar para decodificar o byte do GPIO
def decode_gpio_data(gpio_byte):
    gpio_num = (gpio_byte >> 3) & 0x1F  # Extrai os 5 bits mais significativos (bit 7-3)
    gpio_in_out = (gpio_byte >> 2) & 0x01  # Extrai o sexto bit mais significativo (bit 2)
    gpio_high_low = (gpio_byte >> 1) & 0x01  # Extrai o sétimo bit mais significativo (bit 1)

    gpio_in_out_str = 'in' if gpio_in_out == 1 else 'out'
    gpio_high_low_str = 'high' if gpio_high_low == 1 else 'low'

    return gpio_num, gpio_in_out_str, gpio_high_low_str


if __name__ == "__main__":
    app = GPIODisplay()

    serial_port = "/dev/ttyUSB0"

    stop_event = threading.Event()


    # Thread para ler dados do mock
    reader_thread = threading.Thread(target=read_gpio_data, args=(serial_port, stop_event))
    reader_thread.start()
    app.mainloop()
    reader_thread.join()

    time.sleep(10)




