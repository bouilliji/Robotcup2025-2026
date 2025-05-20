import keyboard

def test(event):
    print(f"Touche : {type(event.name)}")

keyboard.hook(test)
keyboard.wait()
