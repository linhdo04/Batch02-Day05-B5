import { expect, test, type Page, type Route } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000";

type SearchPayload = {
  from_city: string;
  to_city: string;
  date: string;
  pickup_text: string;
  user_location: {
    label: string;
    lat: number;
    lng: number;
  };
  priority: "price" | "time" | "pickup_distance";
  transport_mode: "all" | "bus" | "train" | "flight";
};

type ClarifyPayload = {
  query: SearchPayload;
  choice: "pickup_place" | "bus_operator";
};

type TicketOption = {
  id: string;
  provider: string;
  operator: string;
  from_city: string;
  to_city: string;
  date: string;
  departure_time: string;
  arrival_time: string;
  price_vnd: number;
  pickup_point: string;
  pickup_address: string;
  pickup_distance_km: number;
  booking_url: string;
  maps_url: string;
  rank_reason: string;
};

type AgentResponse = {
  path: "happy" | "low_confidence" | "failure" | "clarification";
  summary: string;
  tickets: TicketOption[];
  web_results: Array<{
    title: string;
    url: string;
    snippet: string;
    source: string;
  }>;
  warning: string | null;
  clarification_question: string | null;
  clarification_options: Array<"pickup_place" | "bus_operator">;
  suggested_dates: string[];
};

const PRICE_TICKETS: TicketOption[] = [
  {
    id: "vx-hn-dn-001",
    provider: "Vexere",
    operator: "Sao Viet Express",
    from_city: "Ha Noi",
    to_city: "Da Nang",
    date: "2026-06-06",
    departure_time: "20:30",
    arrival_time: "08:10",
    price_vnd: 390000,
    pickup_point: "Ben xe My Dinh",
    pickup_address: "20 Pham Hung, My Dinh, Nam Tu Liem, Ha Noi",
    pickup_distance_km: 7.4,
    booking_url: "https://example.com/book/sao-viet-express",
    maps_url: "https://maps.google.com/?q=20%20Pham%20Hung%20Ha%20Noi",
    rank_reason: "Giá thấp nhất trong nhóm nhưng điểm đón xa hơn 5 km."
  },
  {
    id: "mm-hn-dn-002",
    provider: "MoMo Travel",
    operator: "Queen Cafe VIP",
    from_city: "Ha Noi",
    to_city: "Da Nang",
    date: "2026-06-06",
    departure_time: "19:15",
    arrival_time: "07:00",
    price_vnd: 420000,
    pickup_point: "Cau Giay Office",
    pickup_address: "165 Cau Giay, Dich Vong, Cau Giay, Ha Noi",
    pickup_distance_km: 1.2,
    booking_url: "https://example.com/book/queen-cafe-vip",
    maps_url: "https://maps.google.com/?q=165%20Cau%20Giay%20Ha%20Noi",
    rank_reason: "Điểm đón gần nhất, phù hợp khi cần lên xe thuận tiện."
  },
  {
    id: "vx-hn-dn-003",
    provider: "Vexere",
    operator: "Camel Travel",
    from_city: "Ha Noi",
    to_city: "Da Nang",
    date: "2026-06-06",
    departure_time: "21:00",
    arrival_time: "09:20",
    price_vnd: 450000,
    pickup_point: "Tran Khat Chan Pickup",
    pickup_address: "308 Tran Khat Chan, Hai Ba Trung, Ha Noi",
    pickup_distance_km: 3.6,
    booking_url: "https://example.com/book/camel-travel",
    maps_url: "https://maps.google.com/?q=308%20Tran%20Khat%20Chan%20Ha%20Noi",
    rank_reason: "Giá cao hơn một chút nhưng thời gian đi cân bằng."
  }
];

const PICKUP_DISTANCE_TICKETS: TicketOption[] = [
  PRICE_TICKETS[1],
  PRICE_TICKETS[2],
  PRICE_TICKETS[0]
];

const SUGGESTED_DATE_TICKET: TicketOption = {
  id: "mm-hn-nt-001",
  provider: "MoMo Travel",
  operator: "Lien Hung",
  from_city: "Ha Noi",
  to_city: "Nha Trang",
  date: "2026-06-07",
  departure_time: "17:30",
  arrival_time: "13:00",
  price_vnd: 620000,
  pickup_point: "Ben xe Giap Bat",
  pickup_address: "Giai Phong, Hoang Mai, Ha Noi",
  pickup_distance_km: 8.3,
  booking_url: "https://example.com/book/lien-hung",
  maps_url: "https://maps.google.com/?q=Ben%20xe%20Giap%20Bat",
  rank_reason: "Đây là ngày gần nhất còn dữ liệu để user tiếp tục ra quyết định."
};

const WEB_ONLY_RESPONSE: AgentResponse = {
  path: "low_confidence",
  summary: "Tìm thấy nguồn tham khảo từ web cho tuyến này.",
  tickets: [],
  web_results: [
    {
      title: "Vé xe Hà Nội đi Hải Phòng",
      url: "https://example.com/ha-noi-hai-phong",
      snippet: "Có nhiều nhà xe mở bán theo ngày, cần mở nguồn để xem giá và giờ đi chi tiết.",
      source: "Vexere"
    },
    {
      title: "Lịch tàu Hà Nội - Hải Phòng",
      url: "https://example.com/train-ha-noi-hai-phong",
      snippet: "Nguồn tham khảo cho phương án di chuyển thay thế khi không có dữ liệu mock.",
      source: "Google Search"
    }
  ],
  warning: null,
  clarification_question: null,
  clarification_options: [],
  suggested_dates: []
};

const CLARIFICATION_RESPONSE: AgentResponse = {
  path: "clarification",
  summary: "Cần xác nhận ý nghĩa của 'Thanh Phong' trước khi gợi ý vé.",
  tickets: [],
  web_results: [],
  warning: null,
  clarification_question:
    "Bạn muốn được đón tại địa danh Giáo xứ Thanh Phong, hay muốn tìm Nhà xe Thanh Phong?",
  clarification_options: ["pickup_place", "bus_operator"],
  suggested_dates: []
};

const CLARIFY_PICKUP_RESPONSE: AgentResponse = {
  path: "low_confidence",
  summary: "Đã tìm thấy 3 lựa chọn phù hợp nhất theo ưu tiên price.",
  tickets: PRICE_TICKETS,
  web_results: [],
  warning: "Đã xử lý Thanh Phong là địa danh điểm đón. Hãy kiểm tra địa chỉ đầy đủ và Maps trước khi bấm đặt vé.",
  clarification_question: null,
  clarification_options: [],
  suggested_dates: []
};

const CLARIFY_OPERATOR_FAILURE: AgentResponse = {
  path: "failure",
  summary: "Không có Nhà xe Thanh Phong trên chặng/ngày đã chọn.",
  tickets: [],
  web_results: [],
  warning: "Hãy chọn ý nghĩa là địa danh điểm đón nếu bạn đang nói về Giáo xứ Thanh Phong.",
  clarification_question: null,
  clarification_options: [],
  suggested_dates: ["2026-06-07"]
};

function successResponse(body: Partial<AgentResponse>): AgentResponse {
  return {
    path: "happy",
    summary: "Đã tìm thấy 3 lựa chọn phù hợp nhất theo ưu tiên price.",
    tickets: PRICE_TICKETS,
    web_results: [],
    warning: null,
    clarification_question: null,
    clarification_options: [],
    suggested_dates: [],
    ...body
  };
}

async function fulfillJson(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({
    status,
    contentType: "application/json; charset=utf-8",
    body: JSON.stringify(body)
  });
}

async function setupMockApi(page: Page): Promise<void> {
  await page.route("https://nominatim.openstreetmap.org/**", async (route) => {
    const url = new URL(route.request().url());
    const query = url.searchParams.get("q") ?? "";
    if (/cau giay/i.test(query)) {
      await fulfillJson(route, [
        {
          display_name: "Cầu Giấy, Hà Nội, Việt Nam",
          lat: "21.0369",
          lon: "105.7897"
        }
      ]);
      return;
    }

    await fulfillJson(route, []);
  });

  await page.route("**/api/search", async (route) => {
    const payload = route.request().postDataJSON() as SearchPayload;

    if (/thanh phong/i.test(payload.pickup_text)) {
      await fulfillJson(route, CLARIFICATION_RESPONSE);
      return;
    }

    if (payload.to_city === "Hai Phong") {
      await fulfillJson(route, WEB_ONLY_RESPONSE);
      return;
    }

    if (payload.to_city === "Nha Trang" && payload.date === "2026-06-06") {
      await fulfillJson(
        route,
        successResponse({
          path: "failure",
          summary: "Không tìm thấy vé phù hợp cho ngày đã chọn.",
          tickets: [],
          warning: "Không tìm thấy dữ liệu nội bộ hoặc nguồn web từ Tavily. Thử đổi ngày đi hoặc kiểm tra lại tên tuyến.",
          suggested_dates: ["2026-06-07"]
        })
      );
      return;
    }

    if (payload.to_city === "Nha Trang" && payload.date === "2026-06-07") {
      await fulfillJson(
        route,
        successResponse({
          path: "low_confidence",
          summary: "Đã tìm thấy 1 lựa chọn phù hợp nhất theo ưu tiên price.",
          tickets: [SUGGESTED_DATE_TICKET],
          warning: "Chỉ còn 1 lựa chọn; điểm đón cách bạn 8.3 km.",
          suggested_dates: []
        })
      );
      return;
    }

    if (payload.priority === "pickup_distance") {
      await fulfillJson(
        route,
        successResponse({
          path: "low_confidence",
          summary: "Đã tìm thấy 3 lựa chọn phù hợp nhất theo ưu tiên pickup_distance.",
          tickets: PICKUP_DISTANCE_TICKETS,
          warning: null
        })
      );
      return;
    }

    await fulfillJson(
      route,
      successResponse({
        path: "low_confidence",
        summary: "Đã tìm thấy 3 lựa chọn phù hợp nhất theo ưu tiên price.",
        tickets: PRICE_TICKETS,
        warning: "Lựa chọn đứng đầu có điểm đón xa hơn 5 km; hãy mở Maps để xác nhận trước khi đặt."
      })
    );
  });

  await page.route("**/api/clarify", async (route) => {
    const payload = route.request().postDataJSON() as ClarifyPayload;
    if (payload.choice === "pickup_place") {
      await fulfillJson(route, CLARIFY_PICKUP_RESPONSE);
      return;
    }

    await fulfillJson(route, CLARIFY_OPERATOR_FAILURE);
  });

  await page.route("**/api/chat", async (route) => {
    const payload = route.request().postDataJSON() as { message: string };

    if (/da nang 3 ngay 2 dem/i.test(payload.message)) {
      await fulfillJson(route, {
        reply:
          "Gợi ý nhanh: ngày 1 đi Bà Nà hoặc bán đảo Sơn Trà, ngày 2 vào Hội An, ngày 3 dạo biển Mỹ Khê và ăn hải sản."
      });
      return;
    }

    if (/thanh phong/i.test(payload.message)) {
      await fulfillJson(route, {
        reply:
          "Bạn muốn được đón tại địa danh Giáo xứ Thanh Phong hay muốn tìm Nhà xe Thanh Phong?"
      });
      return;
    }

    await fulfillJson(route, {
      reply: "SmartTravel đã nhận câu hỏi của bạn và sẽ gợi ý theo dữ liệu hiện có."
    });
  });
}

async function openHome(page: Page): Promise<void> {
  await setupMockApi(page);
  await page.goto(BASE_URL);
  await expect(page.getByRole("heading", { name: "SmartTravel AI" })).toBeVisible();
}

test.describe("SmartBus/SmartTravel E2E", () => {
  test("tìm vé mặc định, chọn điểm đón từ autocomplete và hiển thị đủ top 3", async ({ page }) => {
    await openHome(page);

    await page.getByTestId("pickup-text").fill("Cau Giay");
    const option = page.getByRole("option", { name: /Cầu Giấy, Hà Nội/i });
    await expect(option).toBeVisible();
    await option.click();

    const searchRequest = page.waitForRequest((request) => request.url().includes("/api/search"));
    const searchResponse = page.waitForResponse((response) => response.url().includes("/api/search"));

    await page.getByTestId("search-submit").click();

    const request = await searchRequest;
    await searchResponse;

    const payload = request.postDataJSON() as SearchPayload;
    expect(payload.user_location.label).toContain("Cầu Giấy");
    expect(payload.priority).toBe("price");

    await expect(page.getByTestId("ticket-card")).toHaveCount(3);
    await expect(page.getByTestId("low-confidence-warning")).toContainText("điểm đón xa hơn 5 km");
    await expect(page.getByTestId("ticket-card").first()).toContainText("Sao Viet Express");
    await expect(page.getByTestId("ticket-price").first()).toContainText("390");
    await expect(page.getByTestId("maps-link").first()).toHaveAttribute("href", /maps\.google\.com/);
    await expect(page.getByTestId("booking-link").first()).toHaveAttribute("href", /example\.com/);
  });

  test("đổi priority sau khi đã search sẽ tự re-rank kết quả", async ({ page }) => {
    await openHome(page);

    await page.getByTestId("search-submit").click();
    await expect(page.getByTestId("ticket-card")).toHaveCount(3);
    await expect(page.getByTestId("ticket-card").first()).toContainText("Sao Viet Express");

    const rerankRequest = page.waitForRequest((request) => {
      if (!request.url().includes("/api/search")) return false;
      const payload = request.postDataJSON() as SearchPayload;
      return payload.priority === "pickup_distance";
    });
    const rerankResponse = page.waitForResponse((response) => response.url().includes("/api/search"));

    await page.getByTestId("priority-pickup_distance").click();

    const request = await rerankRequest;
    await rerankResponse;

    const payload = request.postDataJSON() as SearchPayload;
    expect(payload.priority).toBe("pickup_distance");

    await expect(page.getByTestId("priority-pickup_distance")).toHaveAttribute("aria-pressed", "true");
    await expect(page.getByTestId("ticket-card").first()).toContainText("Queen Cafe VIP");
    await expect(page.getByTestId("ticket-card").first()).toContainText("1.2 km");
  });

  test("case nhập nhằng Thanh Phong yêu cầu clarification và cho phép xác nhận điểm đón", async ({ page }) => {
    await openHome(page);

    await page.getByTestId("pickup-text").fill("Giao xu Thanh Phong");
    await page.getByTestId("search-submit").click();

    await expect(page.getByTestId("clarification-panel")).toBeVisible();
    await expect(page.getByRole("heading", { name: /Giáo xứ Thanh Phong/i })).toBeVisible();

    const clarifyResponse = page.waitForResponse((response) => response.url().includes("/api/clarify"));
    await page.getByTestId("clarify-pickup").click();
    await clarifyResponse;

    await expect(page.getByTestId("clarification-panel")).toHaveCount(0);
    await expect(page.getByTestId("low-confidence-warning")).toContainText("địa danh điểm đón");
    await expect(page.getByTestId("ticket-card")).toHaveCount(3);
  });

  test("nếu chọn Nhà xe Thanh Phong trong sai chặng thì hiển thị failure và suggested date", async ({ page }) => {
    await openHome(page);

    await page.getByTestId("pickup-text").fill("Giao xu Thanh Phong");
    await page.getByTestId("search-submit").click();
    await expect(page.getByTestId("clarification-panel")).toBeVisible();

    const clarifyResponse = page.waitForResponse((response) => response.url().includes("/api/clarify"));
    await page.getByTestId("clarify-operator").click();
    await clarifyResponse;

    await expect(page.getByTestId("failure-panel")).toBeVisible();
    await expect(page.getByTestId("failure-panel")).toContainText("Không có Nhà xe Thanh Phong");
    await expect(page.getByTestId("suggested-date")).toHaveCount(1);
  });

  test("không có vé cho ngày đã chọn thì cho phép chuyển sang suggested date và tải lại kết quả", async ({ page }) => {
    await openHome(page);

    await page.getByTestId("to-city").fill("Nha Trang");
    await page.getByTestId("search-submit").click();

    await expect(page.getByTestId("failure-panel")).toBeVisible();
    await expect(page.getByTestId("failure-panel")).toContainText("Không tìm thấy vé phù hợp");

    const retryRequest = page.waitForRequest((request) => {
      if (!request.url().includes("/api/search")) return false;
      const payload = request.postDataJSON() as SearchPayload;
      return payload.date === "2026-06-07";
    });
    const retryResponse = page.waitForResponse((response) => response.url().includes("/api/search"));

    await page.getByTestId("suggested-date").click();

    const request = await retryRequest;
    await retryResponse;

    const payload = request.postDataJSON() as SearchPayload;
    expect(payload.date).toBe("2026-06-07");

    await expect(page.getByTestId("failure-panel")).toHaveCount(0);
    await expect(page.getByText("2026-06-07")).toBeVisible();
    await expect(page.getByTestId("ticket-card")).toHaveCount(1);
    await expect(page.getByTestId("low-confidence-warning")).toContainText("Chỉ còn 1 lựa chọn");
    await expect(page.getByTestId("ticket-card").first()).toContainText("Lien Hung");
  });

  test("khi không có ticket mock nhưng có nguồn web thì hiển thị web fallback", async ({ page }) => {
    await openHome(page);

    await page.getByTestId("to-city").fill("Hai Phong");
    await page.getByTestId("search-submit").click();

    await expect(page.getByTestId("web-result-list")).toBeVisible();
    await expect(page.getByTestId("web-result-card")).toHaveCount(2);
    await expect(page.getByTestId("web-result-card").first()).toContainText("Vé xe Hà Nội đi Hải Phòng");
    await expect(page.getByRole("link", { name: /Mở nguồn/i }).first()).toHaveAttribute(
      "href",
      /example\.com/
    );
  });

  test("chat assistant nhận prompt gợi ý và trả phản hồi của trợ lý", async ({ page }) => {
    await openHome(page);

    await page.getByRole("button", { name: "Mở trợ lý" }).click();
    await expect(page.getByRole("dialog", { name: "Trợ lý SmartTravel" })).toBeVisible();

    await page.getByRole("button", { name: "Gợi ý lịch trình Đà Nẵng 3 ngày 2 đêm" }).click();
    await expect(page.getByPlaceholder("Hỏi lịch trình, vé, khách sạn...")).toHaveValue(
      "Gợi ý lịch trình Đà Nẵng 3 ngày 2 đêm"
    );

    const chatResponse = page.waitForResponse((response) => response.url().includes("/api/chat"));
    await page.getByRole("button", { name: "Gửi" }).click();
    await chatResponse;

    await expect(page.getByText("Gợi ý lịch trình Đà Nẵng 3 ngày 2 đêm")).toBeVisible();
    await expect(page.getByText("ngày 1 đi Bà Nà hoặc bán đảo Sơn Trà")).toBeVisible();
  });
});
