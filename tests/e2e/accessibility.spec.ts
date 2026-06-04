import { expect, test, type Page, type Route } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000";

type SearchResponse = {
  path: "happy" | "low_confidence" | "failure" | "clarification";
  summary: string;
  tickets: Array<{
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
  }>;
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

const SEARCH_RESPONSE: SearchResponse = {
  path: "happy",
  summary: "Da tim thay 1 lua chon phu hop nhat theo uu tien price.",
  tickets: [
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
      maps_url: "https://example.com/maps/sao-viet-express",
      rank_reason: "Gia tot nhat trong nhom.",
    },
  ],
  web_results: [],
  warning: null,
  clarification_question: null,
  clarification_options: [],
  suggested_dates: [],
};

async function mockApi(route: Route, body: unknown, status = 200): Promise<void> {
  await route.fulfill({
    status,
    contentType: "application/json; charset=utf-8",
    body: JSON.stringify(body),
  });
}

async function openHome(page: Page): Promise<void> {
  await page.goto(BASE_URL);
  await expect(page.getByRole("heading", { name: "SmartTravel AI" })).toBeVisible();
}

test.describe("Accessibility", () => {
  test("exposes semantic landmarks and labeled search controls", async ({ page }) => {
    await openHome(page);

    await expect(page.getByRole("region", { name: "SmartTravel search workspace" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "SmartTravel AI" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Tìm phương án di chuyển" })).toBeVisible();
    await expect(page.getByLabel("Điểm đi")).toBeVisible();
    await expect(page.getByLabel("Điểm đến")).toBeVisible();
    await expect(page.getByLabel("Ngày khởi hành")).toBeVisible();
    await expect(page.getByLabel("Điểm đón, ga, sân bay hoặc ghi chú vị trí")).toBeVisible();
    await expect(page.getByRole("button", { name: "Tìm phương án" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Mở trợ lý" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Giá tốt" })).toHaveAttribute("aria-pressed", "true");
    await expect(page.getByRole("button", { name: "Vị trí tiện" })).toHaveAttribute("aria-pressed", "false");
  });

  test("keeps segmented controls keyboard operable with clear pressed state", async ({ page }) => {
    await openHome(page);

    const timeButton = page.getByRole("button", { name: "Giờ đi" });
    const flightButton = page.getByRole("button", { name: "Máy bay" });

    await timeButton.click();
    await expect(timeButton).toHaveAttribute("aria-pressed", "true");
    await expect(page.getByRole("button", { name: "Giá tốt" })).toHaveAttribute("aria-pressed", "false");

    await flightButton.click();
    await expect(flightButton).toHaveAttribute("aria-pressed", "true");
    await expect(page.getByRole("button", { name: "Xe" })).toHaveAttribute("aria-pressed", "false");
  });

  test("announces results and assistant dialog with accessible names", async ({ page }) => {
    await page.route("**/api/search", async (route) => {
      await mockApi(route, SEARCH_RESPONSE);
    });

    await page.route("**/api/chat", async (route) => {
      await mockApi(route, { reply: "Xin chào, tôi có thể hỗ trợ bạn." });
    });

    await openHome(page);

    await page.getByRole("button", { name: "Tìm phương án" }).click();

    await expect(page.getByRole("heading", { name: "Ha Noi → Da Nang" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Sao Viet Express" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Xem Maps" })).toBeVisible();
    await expect(page.getByRole("link", { name: "Đặt / kiểm tra" })).toBeVisible();

    await page.getByRole("button", { name: "Mở trợ lý" }).click();
    const dialog = page.getByRole("dialog", { name: "Trợ lý SmartTravel" });

    await expect(dialog).toBeVisible();
    await expect(page.getByRole("button", { name: "Đóng trợ lý" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Toàn màn hình" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Gợi ý lịch trình Đà Nẵng 3 ngày 2 đêm" })).toBeVisible();
    await expect(page.getByRole("textbox", { name: /Hỏi lịch trình, vé, khách sạn/i })).toBeVisible();
    await expect(page.getByRole("button", { name: "Gửi" })).toBeVisible();
  });
});