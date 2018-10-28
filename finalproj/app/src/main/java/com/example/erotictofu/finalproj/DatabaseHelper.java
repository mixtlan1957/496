package com.example.erotictofu.finalproj;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;

public class DatabaseHelper extends SQLiteOpenHelper{
    // All Static variables
    private static DatabaseHelper sInstance;

    // Database Version
    private static final int DATABASE_VERSION = 1;

    // Database Name
    private static final String DATABASE_NAME = "MTG_DECKS";

    // Table names
    private static final String TABLE_DECKS = "Decks";

    // Player Table Columns names
    private static final String KEY_DNAME = "deckName";

    public static synchronized DatabaseHelper getInstance(Context context) {
        if (sInstance == null) {
            Log.d("DB", "DB instance created");
            sInstance = new DatabaseHelper(context.getApplicationContext());
        }

        return sInstance;
    }

    private DatabaseHelper(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
        Log.d("DB", "constructor called");

    }

    // Creating Tables
    @Override
    public void onCreate(SQLiteDatabase db) {
        Log.d("DB", "onCreate called");
        // Create Players
        String SQL = "CREATE TABLE IF NOT EXISTS " + TABLE_DECKS + " ("
                + KEY_DNAME + " TEXT PRIMARY KEY);";
        Log.d("DB", SQL);
        db.execSQL(SQL);
    }

    // Upgrading database
    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        Log.d("DB", "onUpgrade called");

        // Drop older table if existed
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_DECKS);

        // Create tables again
        onCreate(db);
    }

    // Adding new deck
    public long addDeck(String dname) {
        Log.d("DB", "addDeck called");

        SQLiteDatabase db = sInstance.getWritableDatabase();

        ContentValues values = new ContentValues();
        values.put(KEY_DNAME, dname); // Deck's name

        // Inserting Row
        long row = db.insert(TABLE_DECKS, null, values);
        db.close(); // Closing database connection
        return row;
    }

    // Getting All Decks
    public List<String> getAllDecks() {
        Log.d("DB", "getAllPlayers called");

        List<String> deckList = new ArrayList<String>();
        // Select All Query
        String selectQuery = "SELECT  * FROM " + TABLE_DECKS;

        SQLiteDatabase db = sInstance.getWritableDatabase();
        Cursor cursor = db.rawQuery(selectQuery, null);

        // looping through all rows and adding to list
        if (cursor.moveToFirst()) {
            do {
                // Adding deck to list
                deckList.add(cursor.getString(0));
            } while (cursor.moveToNext());
        }
        cursor.close();
        db.close(); // Closing database connection
        // return player list
        return deckList;
    }
}

