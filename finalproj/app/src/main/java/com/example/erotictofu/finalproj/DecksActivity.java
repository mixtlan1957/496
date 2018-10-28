package com.example.erotictofu.finalproj;

import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;

public class DecksActivity extends AppCompatActivity {

    Button btnAdd;
    EditText userInput;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_decks);
        btnAdd = (Button) findViewById(R.id.addDeckToSQL);
        userInput = (EditText) findViewById(R.id.editText);

        btnAdd.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String label = userInput.getText().toString();

                if(label.trim().length()>0) {
                    DatabaseHelper.getInstance(getApplicationContext()).addDeck(label);
                    userInput.setText("");
                }
            }
        });

    }





}
