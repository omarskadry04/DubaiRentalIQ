-- Canonical schema, loaded by the Python builder. Run only on an empty database.
PRAGMA foreign_keys=ON;

CREATE TABLE dim_listing (
  listing_id TEXT NOT NULL PRIMARY KEY,
  listing_type TEXT, room_type TEXT, bedrooms INTEGER,
  latitude REAL, longitude REAL, neighborhood TEXT,
  guests REAL, beds REAL, baths REAL, num_reviews REAL, star_rating REAL,
  superhost TEXT, property_type TEXT, host_id TEXT,
  enriched_metadata_available INTEGER NOT NULL
     CHECK (enriched_metadata_available IN (0,1)),
  metadata_source TEXT NOT NULL
);
CREATE TABLE dim_month (
  month_date TEXT NOT NULL PRIMARY KEY,
  year INTEGER, month_number INTEGER CHECK (month_number BETWEEN 1 AND 12),
  month_label TEXT, month_sort INTEGER, year_month TEXT
);
CREATE TABLE fact_listing_month (
  listing_id TEXT NOT NULL,
  month_date TEXT NOT NULL,
  active INTEGER NOT NULL CHECK (active IN (0,1)),
  listing_type TEXT, room_type TEXT, latitude REAL, longitude REAL,
  bedrooms INTEGER, neighborhood TEXT,
  available_days INTEGER, unavailable_days INTEGER,
  occupancy REAL CHECK (occupancy BETWEEN 0 AND 1),
  native_avg_daily_rate REAL CHECK (native_avg_daily_rate >= 0),
  native_revenue REAL CHECK (native_revenue >= 0),
  native_revpar REAL CHECK (native_revpar >= 0), currency TEXT,
  native_booked_rate_avg REAL CHECK (native_booked_rate_avg >= 0),
  same_listing_prev_month INTEGER NOT NULL CHECK (same_listing_prev_month IN (0,1)),
  PRIMARY KEY (listing_id, month_date),
  FOREIGN KEY (listing_id) REFERENCES dim_listing(listing_id),
  FOREIGN KEY (month_date) REFERENCES dim_month(month_date)
);
CREATE TABLE fact_coverage_month (
  month_date TEXT NOT NULL PRIMARY KEY,
  observed_listings INTEGER, active_listings INTEGER,
  neighborhood_missing_pct REAL, bedrooms_missing_pct REAL,
  same_listing_prev_month INTEGER, median_active_adr_aed REAL,
  median_active_estimated_occupancy REAL, coverage_change_pct REAL,
  FOREIGN KEY (month_date) REFERENCES dim_month(month_date)
);
CREATE TABLE fact_peer_benchmark (
  listing_id TEXT NOT NULL, month_date TEXT NOT NULL,
  peer_count INTEGER CHECK (peer_count >= 0), radius_km REAL,
  peer_median_aed REAL, peer_p25_aed REAL, peer_p75_aed REAL,
  peer_median_estimated_occupancy REAL,
  premium_pct REAL, estimated_occupancy_gap_pp REAL,
  comparison_status TEXT, review_signal TEXT, confidence_label TEXT,
  PRIMARY KEY (listing_id, month_date),
  FOREIGN KEY (listing_id, month_date)
    REFERENCES fact_listing_month(listing_id, month_date)
);
CREATE TABLE peer_examples_latest (
  listing_id TEXT NOT NULL, month_date TEXT NOT NULL,
  peer_listing_id TEXT NOT NULL,
  distance_km REAL CHECK (distance_km >= 0),
  peer_adr_aed REAL CHECK (peer_adr_aed >= 0),
  peer_room_type TEXT, peer_bedrooms INTEGER,
  peer_estimated_occupancy REAL CHECK (peer_estimated_occupancy BETWEEN 0 AND 1),
  PRIMARY KEY (listing_id, month_date, peer_listing_id),
  FOREIGN KEY (listing_id, month_date)
    REFERENCES fact_listing_month(listing_id, month_date),
  FOREIGN KEY (peer_listing_id, month_date)
    REFERENCES fact_listing_month(listing_id, month_date)
);
CREATE INDEX idx_fact_month ON fact_listing_month(month_date);
CREATE INDEX idx_benchmark_month ON fact_peer_benchmark(month_date);
-- Composite primary key already indexes (listing_id,month_date); no duplicate index.
CREATE INDEX idx_peer_listing ON peer_examples_latest(peer_listing_id,month_date);
