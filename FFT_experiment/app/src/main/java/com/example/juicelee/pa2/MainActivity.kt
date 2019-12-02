package com.example.juicelee.pa2

import android.Manifest
import android.content.Context
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.content.pm.PackageManager
import android.media.*
import android.os.AsyncTask
import android.support.v4.app.ActivityCompat
import android.util.Log
import com.example.cs442_hw2.FFT
import kotlinx.android.synthetic.main.activity_main.*
import java.io.File
import java.io.FileWriter
import java.lang.Double.max
import java.text.SimpleDateFormat
import java.util.*
import kotlin.math.sin

class MainActivity : AppCompatActivity() {

    private var fileWriter: FileWriter? = null
    private var file: File? = null

    private val DURATION = 1
    private val SAMPLE_RATE = 44100
    @Volatile private var flag = false

    private var record_array = ArrayList<Double>()

    private var PERMISSION_ALL = 1
    private var PERMISSIONS = arrayOf(
        android.Manifest.permission.RECORD_AUDIO,
        android.Manifest.permission.READ_EXTERNAL_STORAGE,
        android.Manifest.permission.WRITE_EXTERNAL_STORAGE
    )

    private fun setup_file(){

        if(fileWriter != null){
            fileWriter!!.flush()
            fileWriter!!.close()
        }

        val sdf = SimpleDateFormat("MMdd_HHmmss")
        val currentDateandTime = sdf.format(Date())

        val baseDir = android.os.Environment.getExternalStorageDirectory().absolutePath
        val fileName = "$currentDateandTime.txt"
        val filePath = baseDir + File.separator + fileName
        file = File(filePath)
        fileWriter = FileWriter(file)
//        try {
//            dos = DataOutputStream(BufferedOutputStream(FileOutputStream(file)))
//        } catch (e: Exception) {
//            e.printStackTrace()
//        }
    }

    private fun checkPermissions(permissions: Array<String>): Boolean {
        for(permission in permissions) {
            if(ActivityCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                Log.d("asdfasf","sdfasdfsfdas")
                ActivityCompat.requestPermissions(this, arrayOf(permission), PERMISSION_ALL)
                return false
            }
        }
        return true
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if(grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            return
        } else {
            checkPermissions(PERMISSIONS)
        }
        return
    }

    private lateinit var recorder: AudioRecord

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        checkPermissions(PERMISSIONS)

        setup_file()

        recorder = AudioRecord(MediaRecorder.AudioSource.MIC, 44100,
            AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, 1024)
        recorder.startRecording()

        val audioManager = this.applicationContext.getSystemService(Context.AUDIO_SERVICE) as AudioManager
        val max_vol = audioManager.getStreamMaxVolume(AudioManager.STREAM_VOICE_CALL);
        audioManager.setStreamVolume(AudioManager.STREAM_VOICE_CALL, max_vol, AudioManager.FLAG_SHOW_UI)

        var numSamples = DURATION*SAMPLE_RATE
        val samples = DoubleArray(numSamples)
        val buffer = ShortArray(numSamples)
        val freq = 20000

        for (i in 0 until numSamples) {
            samples[i] = sin(2.0 * Math.PI * i.toDouble() * freq / SAMPLE_RATE)
            buffer[i] = (samples[i] * Short.MAX_VALUE).toShort()
        }

        load_button.setOnClickListener {
            val baseDir = android.os.Environment.getExternalStorageDirectory().absolutePath
            val fileName = "1202_230925.txt"
            val filePath = baseDir + File.separator + fileName

            var buf = File(filePath).bufferedReader().readLines().map{it.toShort()}
            for(i in 0 until buf.size/512){
                var curbuf = buf.subList(i*512,(i+1)*512).toShortArray()
                val fftresult = FFT(512).getFreqSpectrumFromShort(curbuf)
                var max = 0.0
                var maxidx = 0
                for(i in 0 until fftresult.size){
                    if(max < fftresult[i]){
                        max = fftresult[i]
                        maxidx = i
                    }
                }

                Log.d("max", maxidx.toString())
                Log.d("maxvalue", max.toString())
            }


        }

        my_button.setOnClickListener {
            val at = AudioTrack(
                AudioManager.STREAM_VOICE_CALL,
                SAMPLE_RATE,
                AudioFormat.CHANNEL_OUT_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                buffer.size,
                AudioTrack.MODE_STATIC
            )
            flag = true
            Thread.sleep(1000)
            at.write(buffer, 0, buffer.size)
            at.play()
        }

        Thread(Runnable {
            while(true) {
                if(flag) {
                    val buf = ShortArray(264600)
                    recorder.read(buf, 0, 264600)
                    fileWriter!!.write(buf.joinToString("\n"))
                    fileWriter!!.flush()
                    flag = false
                }
            }
        }).start()
    }
}
