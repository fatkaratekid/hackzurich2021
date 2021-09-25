using UnityEngine;
using System;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.IO;

public class PlayerController: MonoBehaviour
{

	// 1. Declare Variables
	Thread receiveThread; //1
	UdpClient client; //2
	int port; //3

	// public GameObject Player; //4
	// AudioSource jumpSound; //5
	// bool jump; //6

	// 2. Initialize variables
	void Start () 
	{
		port = 5065; //1 
		// jump = false; //2 
		// jumpSound = gameObject.GetComponent<AudioSource>(); //3

		InitUDP(); //4
        print("start player controller");
	}

	// 3. InitUDP
	private void InitUDP()
	{
		print ("UDP Initialized");

		receiveThread = new Thread (new ThreadStart(ReceiveData)); //1 
		receiveThread.IsBackground = true; //2
		receiveThread.Start (); //3

	}

	// 4. Receive Data
	private void ReceiveData()
	{
		client = new UdpClient (port); //1
		while (true) //2
		{
			try
			{
				IPEndPoint anyIP = new IPEndPoint(IPAddress.Parse("0.0.0.0"), port); //3
				byte[] data = client.Receive(ref anyIP); //4

				string text = Encoding.UTF8.GetString(data); //5
				print (">> " + text);
                // GetSampleFrame(text);

				// jump = true; //6

			} catch(Exception e)
			{
				print (e.ToString()); //7
			}
		}
	}


    // private void GetSampleFrame(string text)
    // {
    //     using (StreamWriter writer = new StreamWriter('sampleFrame.txt'))  
    //     {  
    //         writer.WriteLine(text);
    //     } 
    // }

	// // 5. Make the Player Jump
	// public void Jump()
	// {
	// 	Player.GetComponent<Animator>().SetTrigger ("Jump"); //1
	// 	jumpSound.Play(44100); // Play Jump Sound with a 1 second delay to match the animation
	// }

	// 6. Check for variable value, and make the Player Jump!
	void Update () 
	{
		// if(jump == true)
		// {
		// 	// Jump ();
		// 	// jump = false;
		// 	print('jump!!')
		// }
        print("update player controller");
	}
}
