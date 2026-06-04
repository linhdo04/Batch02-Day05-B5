/**
 * Route Map Component - Hiển thị bản đồ tuyến đường với pickup và destination
 * 
 * Component này có thể hiển thị:
 * - Bản đồ nhỏ trong ticket card (compact mode)
 * - Bản đồ lớn trong modal/sidebar (full mode)
 */

import { useState } from "react";
import { X, Maximize2 } from "lucide-react";
import { MapEmbed } from "./MapEmbed";

type RouteMapProps = {
  /** Tọa độ điểm đón */
  pickup: { lat: number; lng: number };
  /** Tọa độ điểm đến */
  destination: { lat: number; lng: number };
  /** Tên điểm đón */
  pickupName: string;
  /** Tên điểm đến */
  destinationName: string;
  /** Chế độ hiển thị (compact | full) */
  mode?: "compact" | "full";
  /** Có thể mở rộng thành modal không */
  expandable?: boolean;
};

export function RouteMap({
  pickup,
  destination,
  pickupName,
  destinationName,
  mode = "compact",
  expandable = true
}: RouteMapProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const height = mode === "compact" ? 200 : 400;

  return (
    <>
      <div style={{ position: 'relative', marginTop: '16px' }}>
        <MapEmbed
          pickup={pickup}
          destination={destination}
          pickupName={pickupName}
          destinationName={destinationName}
          height={height}
          mode="directions"
        />
        
        {expandable && mode === "compact" && (
          <button
            onClick={() => setIsExpanded(true)}
            style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              background: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              padding: '8px',
              cursor: 'pointer',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
            aria-label="Mở rộng bản đồ"
          >
            <Maximize2 size={16} />
          </button>
        )}
      </div>

      {/* Modal hiển thị bản đồ lớn */}
      {isExpanded && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '20px'
          }}
          onClick={() => setIsExpanded(false)}
        >
          <div
            style={{
              background: 'white',
              borderRadius: '12px',
              maxWidth: '900px',
              width: '100%',
              maxHeight: '90vh',
              overflow: 'hidden',
              position: 'relative'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                padding: '16px',
                borderBottom: '1px solid #e5e7eb',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div>
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>
                  Chỉ đường
                </h3>
                <p style={{ margin: '4px 0 0', fontSize: '14px', color: '#6b7280' }}>
                  {pickupName} → {destinationName}
                </p>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '8px',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center'
                }}
                aria-label="Đóng"
              >
                <X size={20} />
              </button>
            </div>
            
            <div style={{ height: 'calc(90vh - 80px)' }}>
              <MapEmbed
                pickup={pickup}
                destination={destination}
                pickupName={pickupName}
                destinationName={destinationName}
                height={600}
                mode="directions"
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
}
