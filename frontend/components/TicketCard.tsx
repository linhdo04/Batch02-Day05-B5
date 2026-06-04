import { ArrowUpRight, Clock, MapPinned, Ticket, Map } from "lucide-react";
import { useState } from "react";

import { formatCurrency } from "@/lib/format";
import type { TicketOption } from "@/lib/types";
import { RouteMap } from "./RouteMap";

type TicketCardProps = {
  ticket: TicketOption;
  rank: number;
  /** Tọa độ điểm đón người dùng */
  userLocation?: { lat: number; lng: number };
};

export function TicketCard({ ticket, rank, userLocation }: TicketCardProps) {
  const [showMap, setShowMap] = useState(false);

  // Parse tọa độ điểm đón từ ticket (giả sử backend trả về)
  // Nếu không có, dùng fallback
  const pickupCoords = ticket.pickup_lat && ticket.pickup_lng
    ? { lat: ticket.pickup_lat, lng: ticket.pickup_lng }
    : userLocation || { lat: 10.7769, lng: 106.7009 }; // Fallback: TP.HCM

  // Điểm đến mặc định (có thể lấy từ query hoặc ticket)
  const destinationCoords = { lat: 10.7769, lng: 106.7009 }; // TP.HCM

  return (
    <article className="ticket-card" data-testid="ticket-card">
      <div className="ticket-rank" aria-label={`Rank ${rank}`}>
        {rank}
      </div>

      <div className="ticket-main">
        <div className="ticket-title">
          <div>
            <p className="provider">{ticket.provider}</p>
            <h3>{ticket.operator}</h3>
          </div>
          <strong data-testid="ticket-price">{formatCurrency(ticket.price_vnd)}</strong>
        </div>

        <div className="metric-row">
          <span>
            <Clock aria-hidden="true" size={16} />
            {ticket.departure_time} → {ticket.arrival_time}
          </span>
          <span>
            <MapPinned aria-hidden="true" size={16} />
            {ticket.pickup_distance_km.toFixed(1)} km
          </span>
        </div>

        <div className="pickup-block">
          <p>{ticket.pickup_point}</p>
          <span>{ticket.pickup_address}</span>
        </div>

        <p className="rank-reason">{ticket.rank_reason}</p>

        {/* Hiển thị bản đồ nếu người dùng click "Xem bản đồ" */}
        {showMap && (
          <RouteMap
            pickup={pickupCoords}
            destination={destinationCoords}
            pickupName={ticket.pickup_point}
            destinationName="Điểm đến"
            mode="compact"
            expandable={true}
          />
        )}

        <div className="ticket-actions">
          <button
            onClick={() => setShowMap(!showMap)}
            style={{
              background: 'none',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              padding: '8px 12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '14px',
              fontWeight: 500,
              color: showMap ? '#3b82f6' : '#374151'
            }}
          >
            <Map aria-hidden="true" size={16} />
            {showMap ? 'Ẩn bản đồ' : 'Xem bản đồ'}
          </button>
          <a data-testid="maps-link" href={ticket.maps_url} rel="noreferrer" target="_blank">
            <MapPinned aria-hidden="true" size={16} />
            Google Maps
          </a>
          <a data-testid="booking-link" href={ticket.booking_url} rel="noreferrer" target="_blank">
            <Ticket aria-hidden="true" size={16} />
            Đặt / kiểm tra
            <ArrowUpRight aria-hidden="true" size={14} />
          </a>
        </div>
      </div>
    </article>
  );
}
