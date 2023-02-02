# Reverse_Shell
Reverse shell script on python

First of all you may not install colorama and tqdm because that used only for cute progress bar when you are downloading files from client so if you
will comment or delete line 12 (import tqdm) and line 52 you will be able run script without installing requirements.txt
I wrote this script because I'm interested in socket programming and different shell tricks so I hope you won't use it with bad ideas in mind

Also may to note that every result message is sending according to simple rules (protocol one level up than tcp/ip) every packet contains 300 bytes if there
are less than 300 bytes message sends in format msg = msg + b" " * (300 - len(msg)) and flag_to_stop = True after which sends stop_msg to server to stop receive and 
input new command so you can change that concept of sending packets on your own

Also to write in file or append in file if there any text use custom command wtf(IMPORTANT TO STOP WRITING WRITE LINE exit0) 
to create file use custom command ctf and finally to read files insides use custom command read for changing working directory use standart command cd

------------------------------------------------------------------------PARAMS FOR SHELL----------------------------------------------------------------------------------

=======================================================================PARAMS FOR CMD PROMPT==============================================================================
Now little bit about shell params you can use (you can use python main.y --help but maybe it would be comfortable to read it here)
-t, -p uses to specify IPV4 and port on which server will be bind and client will be connect by the standart it's localhost(127.0.0.1)and 5555 just to test script working
-s uses to run script in server mode (REMEMBER IT'S reverse shell means that client which would connect to server will execute commands sending from server)
=======================================================================PARAMS FOR FILES===================================================================================
-up uses for specify that work will be with uploading for client and downloading for server
-abp uses to specify path to file which would send to server only for client option
-nf uses to specify name for file which server would getting from client only for server option
-updr not ready command but in future to upload/download not only single file but whole directory
EXAMPLE: 
python main.py -s -up -nf saving_this_secret_file.txt
python main.py -up -abp C:/Users/mega_ultra_user/Super_secret.txt
=======================================================================================================================================================================

------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Also think will be important to say that on windows and linux are different shell output encoding so there can be little bit problems sometimes with connecting because
server receive the correct encoding (you can find in script variable DECODING_CONST) threw user datagram protocol so don't be angry if script will run not from first
attemp if you have an idea how to make DECODING_CONST without bicycle wich I create in script I will be happy if you will write it to me

All in all despite the fact that it is not very mega super ultra puper script I think that it is really powerfull weapon because this script can create read and write
files and execute gived commands)))
that's enough to make something interesting if target computer will connect to your server(how to make it I think if you are reading this you may already know)

