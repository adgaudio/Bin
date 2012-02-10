#!/usr/bin/env ruby
require "LightCsv"
require "CSV"
require 'benchmark'


#age_buckets = "data/dev_ages.csv"
#states = "data/dev_states.csv"
#genders = [1,2]
interests = "data/dev_interests.csv"
age_buckets = "data/ages.csv"
genders = [1,2]
states = "data/statecoordinates.csv"
#interests = "data/cleanusinterests.csv"


age_buckets = CSV.readlines(age_buckets)
states = CSV.readlines(states)
header = ["keywords", "genders", "age_min", "age_max", "states", "latitude", "longitude"]
CSV.open("./output.csv", 'wb') do |csv|
  csv << header

  LightCsv.foreach(interests) do |interest|
    interest.product(genders, age_buckets, states).each do |c|
      begin
        csv << [c[0], c[1], c[2][0], c[2][1], c[3][0], c[3][1], c[3][2]]
      rescue Exception => e
        puts "Could not handle '#{interest[0]}': #{e}"
        next
      end
    end
  end
end
