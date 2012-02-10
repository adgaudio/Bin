#!/usr/bin/env ruby

require "Mongoid"
require "LightCsv"

MONGO_DB = 'testing'
FILENAME = ARGV.first || "data/cross_product.csv"

_CHUNK_SIZE = 400 # tested optimum

Mongoid.configure do | c|
c.master = Mongo::Connection.new.db(MONGO_DB)
c.logger = false
c.max_retries_on_connection_failure = 3
end

class TargetingSpec
  include Mongoid::Document
  include Mongoid::Timestamps
end

csv = LightCsv.open(FILENAME)
header = csv.first
csv.each_slice(_CHUNK_SIZE) do |batch|
  batch.collect!{|row| Hash[header.zip(row)]}
  TargetingSpec.collection.insert(batch)
end

