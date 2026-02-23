-- DepoSafety V2 Database Schema
-- Run this in your Supabase SQL Editor to create the necessary tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'tenant' CHECK (role IN ('admin', 'inspector', 'landlord', 'tenant')),
    phone VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Properties table
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) DEFAULT 'US',
    property_type VARCHAR(50) DEFAULT 'apartment' CHECK (property_type IN ('apartment', 'house', 'commercial', 'storage')),
    description TEXT,
    square_feet DECIMAL(10,2),
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Scans/Inspections table
CREATE TABLE scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    inspector_id UUID REFERENCES users(id) ON DELETE SET NULL,
    inspection_type VARCHAR(50) DEFAULT 'routine' CHECK (inspection_type IN ('move_in', 'move_out', 'routine', 'damage')),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    notes TEXT,
    video_url TEXT,
    video_key TEXT,
    model_3d_url TEXT,
    blockchain_tx_hash VARCHAR(255),
    metadata_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_properties_owner_id ON properties(owner_id);
CREATE INDEX idx_scans_property_id ON scans(property_id);
CREATE INDEX idx_scans_inspector_id ON scans(inspector_id);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_scans_blockchain_tx ON scans(blockchain_tx_hash);

-- Row Level Security (RLS) policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
CREATE POLICY "Users can read own data" ON users
    FOR SELECT USING (auth.uid() = id);

-- Users can update their own data
CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Property owners can manage their properties
CREATE POLICY "Owners can manage properties" ON properties
    FOR ALL USING (auth.uid() = owner_id);

-- Users can view properties they inspect
CREATE POLICY "Inspectors can view properties" ON properties
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM scans 
            WHERE scans.property_id = properties.id 
            AND scans.inspector_id = auth.uid()
        )
    );

-- Scan policies
CREATE POLICY "Inspectors can manage their scans" ON scans
    FOR ALL USING (auth.uid() = inspector_id);

CREATE POLICY "Property owners can view scans" ON scans
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM properties 
            WHERE properties.id = scans.property_id 
            AND properties.owner_id = auth.uid()
        )
    );

-- Functions for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scans_updated_at BEFORE UPDATE ON scans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
