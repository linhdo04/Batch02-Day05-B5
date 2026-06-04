import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E configuration for SmartTravel AI prototype.
 * Tests run against the Next.js frontend (http://127.0.0.1:3000).
 * API calls are intercepted via page.route() inside each spec file,
 * so no real backend is required to run the suite.
 */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  timeout: 30_000,
  expect: { timeout: 8_000 },

  reporter: [
    ["list"],
    ["html", { outputFolder: "docs/playwright-report", open: "never" }]
  ],

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:3000",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    actionTimeout: 10_000,
    navigationTimeout: 20_000
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] }
    }
  ],

  /* Start Next.js dev server automatically when running tests locally */
  webServer: {
    command: "npm --prefix frontend run dev",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: true,
    timeout: 60_000
  }
});
