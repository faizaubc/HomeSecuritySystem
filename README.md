3.2 Software Design: 
3.2.1 Base Station Software
In the software side of the base station is written in Python using the Python IDE compiler. 
The Raspberry Pi night vision camera code is written as a separate file and is then imported into the main program.
The SMTP protocol to save a picture is also written in a separate file and is imported to the main program.
The main program also has libraries imported for Bluetooth and threading.
The program starts by using pressing a push button switch. If the push button switch is not pressed the alarm is not enabled. 
There is an callback function that sets the Boolean variable to true when the enable push-button is pressed. 
The main program then has a while loop that calls “check motion”, “check camera” or “check door sensor” functions repeatedly

When the motion is triggered , camera detects the motion or door is opened the program enters the required function accordingly and enables the alarm. 
The alarm will keep beeping depending on the what triggered it and will only disable when user presses the push button again to disable the alarm.
Each function checks for the Boolean variable “IsAlarmed” and if the motion is detected, the program updates the LCD screen accordingly.
The length of the buzzer is dependent on the type of motion that triggered it.
For example, if picture is taken the buzzer gives 0.1 second beeps three times.
The program for motion sensor for camera simple compares two instances of images pixel by pixel and returns true or 
false indicating the change in the pixel colors. The sensitivity or the amount of pixel changed in order for the motion to be 
detected is set by sensitivity level constant in the beginning of the program. 
The program also lets the user exclude the regions where there is trees constantly moving that could set the alarm.
The program for SMTP simply connects to the user’s email that is hardcoded in the program and sends an email to the address when 
the camera detects that there is a person at the front or the back door. The path of the picture is passed to the program to indicate
 where to retrieve the saved file. This way it can be extracted then emailed to the user.

3.2.1.1 Base Station: PIR Sensor Software
PIR Sensor code initializes in the main program by setting the output pin on PIR sensor as a 
GPIO input because we are reading data from the output of sensor pin. Then there is a call to the function 
“check motion movement” in the main while loop. If the output pin on the sensor indicated a high that means there is motion detected.
See the Figure 13 below that shows the method written in python. 
The buzzer is set as a output GPIO pin and the value is written to it.
This way a value of high or low can turn the buzzer on and off easily. Before writing to the LCD, a threading functionality lock (displaylock.acquire)
is used so that LCD screen is not overwritten and a garbage value is not displayed.
Figure 13: PIR Sensor Method triggers alarm upon motion detection
The LCD is cleared and then written to. The PIR Sensor causes the buzzer to trigger for 1 second on every iteration in 
the while loop till the push button disables the alarm or user leaves the sensitivity area.

3.2.1.2 Base Station : LCD Display
The LCD Module is initialized by importing a RPLCD library. Then the pins are initialized as data pins, enable pin, 
reset pin, and the numbering mode is set. The numbering mode can be either board mode or pin mode for Raspberry Pi pin configuration.
 Throughout the main program if the alarm is triggered by opening a door, motion sensor, or by motion detected by camera, 
the LCD screen is updated accordingly. Every time the LCD screen is updated, the lock is used from the threading library to make sure that 
the LCD screen does not overlap the data. Once the screen is written to the lock is released. If a new data is to be written to the LCD, 
it is cleared first.

3.2.1.3 Base Station Software: Night Vision Camera Software
The motion detection implemented using Raspberry Pi camera involves capturing two images and comparing each one of them to see if there
is any change in sensitivity. In this program, the sensitivity is set to 20 meaning if 20 pixels are changed that means there is motion detected. 
It compares the pictures pixel by pixel to detect a change. This motion detection is in an entire different file that has a
function called motion returning a Boolean expression indicating if the pixels are different from one image to another. 
In the main program this is imported as a library and the function motion is called to check if motion is detected.
The Figure 14 shows a snippet of the code entering a for loop that compares a picture pixel by pixel.
Figure 14 Raspberry Pi motion detection loop comparing image pixel by pixel

In the main program the “check camera” function repeatedly checks if there is a change in picture by calling the motion function 
from the imported code. The Figure 15 shows the “check camera” function implemented in the main program.
If there is motion detected, a current timestamp is obtained and the picture is saved at a current directory. 
The picture is saved with the timestamp so the user can identify which picture was taken at particular time. 
The capture image function does this procedure and stores the image in the given path along with the timestamp.
Figure 15 Check Camera function the main program constantly calls upon this to detect motion
The capture image is called withing the check camera function. In addition, in the capture image function as shown in Figure 16,
the email code is called and the image is emailed using SMTP protocol. When capturing the image, the buzzer beeps three times very 
quickly to indicate the picture has been captured and emailed to the user.
Figure 16 Capture Image function saves the picture to the specified directory and calls the email code to send a email with
a picture if motion is detected

3.2.1.4 Base Station Software: Push Button Software
The initialization of the push button involves setting the push buttons with software implemented pull-up resistor. 
The Figure 17 shows the software implemented pull up resistors. Both of the push buttons are set as GPIO inputs as the data is read from them.
Figure 17: Initialization of Push Button inputs as GPIO
A callback function was necessary that was detected on the rising edge. If the call back function was not implemented then,
there would be switch debouncing leading to the function being called many times within small framework.
To avoid that callback functions were necessary so that whenever there is a rising edge on either buttons a 
function will be called that will enable or disable the alarm. Figure 18 shows the initialization of callback 
functions on the rising edge meaning when the button is pressed.
Figure 18: Callback Functions on Rising Edge of the Clock for push buttons
Once the call back functions are triggered, the LCD screen is updated accordingly indicating the alarm is enabled/disabled 
and the Boolean flag “IsAlarmed” is set. If the alarm is disabled, then the buzzer is also written a low to turn it off.
The LCD as per usual is locked to make sure there is no data overridden. Figure 19 shows both the call back functions as
described above for push buttons.
Figure 19: Alarm Enable/Disable with Push Button 3.2.2 Bluetooth Station Design Software The ESP32 GPIO pin checks for high or 
low voltage depending on door senor being open or closed. The C++ code inside the ESP32 microcontroller checks for door state change every 300
milliseconds. Upon a state change ( door sensor going from open to close or close to open), the Bluetooth serial protocol sends a character
'c' or 'o' over the Bluetooth to any client listening to it. Once Raspberry Pi main program runs, it makes a serial connection to
the ESP32 microcontroller Bluetooth chip. The main program uses another thread to receive 'c' and 'o' messages from ESP32 Bluetooth
module and puts them into a queue. The queue is checked in the main program to see if a new message is received from the door sensor.
Depending on the message that the main program removes from the queue, the main program displays the message on the LCD screen and beeps 
3 times if the door is opened and 2 times if the door is closed. The need for thread to receive messages from ESP32 Bluetooth was needed as 
python Bluetooth library (pybluez) receive function is a blocking call (does not allow the new statement in the program to execute). 
If it is in our main program, it will block other operations like motion detection and writing to the LCD screen which will make the
system behavior incorrect. The Figure 20 shows the Bluetooth class in the main program. This initializes the main connection with the Bluetooth protocol.
Figure 20 Bluetooth Class in main Program 3.2.3 Integration Integration of PIR Sensor, LCD, Push Buttons, and Camera Module was successfully achieved. 
The main program constantly calls upon checking the output of the PIR Sensor, queue of data received over the Bluetooth and the change in pictures
using camera code. Each sensor has its own function. Inside each function, if the motion is detected, LCD is locked and the data is updated accordingly. 
In addition each sensor has a unique was of setting a buzzer. The alarm continuously keeps ringing till the
user decides to turn it off. In terms of integration, the hardest element to integrate was Bluetooth module. 
This was the biggest obstacle that was overcome using threading. The biggest issue was adding the Bluetooth module to the main program 
that initially caused a blocking call. If the Bluetooth receive function is inside the main while loop it waits till the door is opened. 
Thus, the rest of the functions are not called. This was one of the greatest hindrance in the project. This required some research and a
 conclusion was made to use a separate thread to see the messages from ESP-32 microcontroller. The thread will continuously check for messages 
being received from the ESP-32 Bluetooth module and store them in the queue. The main program will only check the queue to see if there are any
 received messages. If the door or window is opened, there will be an “open message” inside the queue and thus that will trigger the alarm to beep 
three times indicating that the door is opened. Once this was achieved the project was able to run cohesively together in the main program.