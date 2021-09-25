using UnityEngine;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.IO;
using UnityEngine.UI;

public class PlayerController: MonoBehaviour
{
#region Initialization

    public GameObject DrumHandLeft;
    public GameObject DrumHandRight;

    Thread receiveThread; //1
	UdpClient client; //2
	int port; //3
    private Camera cam;
    private string receivedText;
    private string lastReceivedText;

    public class BodyCoordinates
    {
        public float left_hand_x;
        public float left_hand_y;
        public float right_hand_x;
        public float right_hand_y;
    }
    private BodyCoordinates bodyCoordinates;

    private void Awake()
    {
        receivedText = "";
        lastReceivedText = "";
        bodyCoordinates = new BodyCoordinates();
        cam = Camera.main;
    }

	void Start () 
	{
		port = 5065; //1 

		InitUDP(); //4
	}

	private void InitUDP()
	{
		print ("UDP Initialized");

		receiveThread = new Thread (new ThreadStart(ReceiveData)); //1 
		receiveThread.IsBackground = true; //2
		receiveThread.Start (); //3

	}
#endregion


#region data streaming
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

                receivedText = text;

			} catch(Exception e)
			{
				print (e.ToString()); //7
			}
		}
	}
#endregion


	void Update () 
	{
        if (receivedText != lastReceivedText)
        {
            GetCoordinates(receivedText);
            MoveHands();
            lastReceivedText = receivedText;
        }
	}

#region body control

    private void GetCoordinates(string receivedText)
    {
        string[] coordinates = receivedText.Split(' ');
        // TODO: validate incoming data structure
        float left_hand_x = float.Parse(coordinates[1]);
        float left_hand_y = float.Parse(coordinates[3]);
        float right_hand_x = float.Parse(coordinates[5]);
        float right_hand_y = float.Parse(coordinates[7]);
        print("raw x: " + left_hand_x + "raw y: " + left_hand_y);

        bodyCoordinates.left_hand_x = Screen.width * left_hand_x;
        bodyCoordinates.left_hand_y = Screen.height * (1 - left_hand_y);
        bodyCoordinates.right_hand_x = Screen.width * right_hand_x;
        bodyCoordinates.right_hand_y = Screen.height * (1 - right_hand_y);
        print("converted x: " + bodyCoordinates.left_hand_x + "converted y: " + bodyCoordinates.left_hand_y);

    }

    private void MoveHands()
    {
        DrumHandLeft.transform.position = cam.ScreenToWorldPoint(
            new Vector3(bodyCoordinates.left_hand_x, 
                        bodyCoordinates.left_hand_y,
                        cam.transform.position.z + 80)
        );
        DrumHandRight.transform.position = cam.ScreenToWorldPoint(
            new Vector3(bodyCoordinates.right_hand_x,
                        bodyCoordinates.right_hand_y,
                        cam.transform.position.z + 80)
        );

    }

#endregion
}
