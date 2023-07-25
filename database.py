#!/usr/bin/env python3
import sqlite3


class Databases:
  @staticmethod
  def PoliceDB():
    con = sqlite3.connect(".database/PoliceDB.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS Police_Details(Name varchar, Rank varchar, Police_ID varchar, DOB varchar, State varchar, District varchar, Branch varchar, Gender varchar, PhNo varchar, EmailId varchar)")
    cur.execute("CREATE TABLE IF NOT EXISTS Police_Login(Police_ID varchar, Password varchar, Re_Password varchar)")
    con.commit()
    con.close()

  @staticmethod
  def CriminalDB():
    con = sqlite3.connect(".database/CriminalDB.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS Criminal_Details(Name varchar, ID varchar, Age varchar, Gender varchar, Phone_number varchar, Address varchar, No_of_cases varchar, No_of_yrs_prisoned varchar, Case_history varchar)")
    con.commit()
    con.close()
