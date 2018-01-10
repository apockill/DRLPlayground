using UnityEngine;
using System.Collections;
using System.IO;

using System.Net.Sockets;
using System;


public class ScreenCapture : MonoBehaviour {

    internal Boolean socketReady = false;

    public String Host = "localhost";
    public Int32 Port = 1234;
    public TcpClient mySocket;
    NetworkStream theStream;
    StreamWriter theWriter;
    StreamReader theReader;
     


    // Take a shot immediately
    public void Start()
    {
        //mySocket.SendBufferSize = 52164;
        setupSocket();
        //mySocket.SendBufferSize = 60000;
        StartCoroutine(write());
        //File.WriteAllBytes(Application.dataPath + "/../SavedScreen.png", bytes)
        //String s = readSocket ();
        //if (s != "") {
        //	byte[] bytes2 = System.Convert.FromBase64String (s);
        //	File.WriteAllBytes (Application.dataPath + "/../working.png", bytes2);
        //}
    }
    public void Update()
    {
        StartCoroutine(write());
        //String s = readSocket ();
        //if (s != "") {
        //			Debug.Log (s);
        //		}

    }


    public IEnumerator write()
    {
        //Debug.Log ("i");
        yield return new WaitForEndOfFrame();

        Debug.Log("Past first yield");

        int width = Screen.width;
        int height = Screen.height;
        Debug.Log("width" + width);
        Debug.Log("height" + height);
        Texture2D tex = new Texture2D(width, height, TextureFormat.RGB24, false);

        // Read screen contents into the texture
        tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
        tex.Apply();

        // Encode texture into PNG
        //byte[] bytes = new byte[52156];
        byte[] bytes = tex.EncodeToPNG();
        //int len = bytes.GetLength ();
        Debug.Log(bytes.Length);
        //Debug.Log (bytes);
        String rpcText = System.Convert.ToBase64String(bytes);
        Debug.Log("Length of mesage" + bytes.Length);
        Debug.Log(rpcText.Length);
        theWriter.Write(rpcText.Length);
        theWriter.Flush();
        //Debug.Log ("1");
        //String str = System.Text.Encoding.Unicode.GetString(tex.EncodeToPNG());
        //byte[] bytes2 = System.Convert.FromBase64String (rpcText);
        int k = (rpcText.Length) / 1024;
        int j = (rpcText.Length) % 1024;
        //File.WriteAllBytes (Application.dataPath + "/../../../bull.png", bytes);
        int i = 0;
        for (i = 0; i < k; i++)
        {
            String temp = rpcText.Substring(i * 1024, 1024);
            theWriter.Write(temp);
            theWriter.Flush();
        }


        String temp2 = rpcText.Substring(i * 1024, j);
        theWriter.Write(temp2);
        theWriter.Flush();
        yield return new WaitForSeconds(1.0f);

    }


    public void setupSocket()
    {
        try
        {
            mySocket = new TcpClient(Host, Port);

            theStream = mySocket.GetStream();
            //mySocket.SendBufferSize=60000;
            theWriter = new StreamWriter(theStream);
            theReader = new StreamReader(theStream);
            socketReady = true;
            //Debug.Log("k");
        }
        catch (Exception e)
        {
            Debug.Log("Socket error: " + e);
        }
    }


    public String readSocket()
    {
        if (!socketReady)
            return "";
        if (theStream.DataAvailable)
            Debug.Log(theReader.ReadLine());
        return theReader.ReadLine();
    }
}
