
import { useEffect, useMemo, useState } from "react";
import {
  AreaChart,
  BarChart,
  Card,
  Metric,
  Text,
  Title,
} from "@tremor/react";

const sourceColors = {
  github: "bg-slate-800",
  slack: "bg-purple-500",
  jira: "bg-blue-500",
  ide: "bg-emerald-500",
};

const navigation = [
  "Overview",
  "Developer Activity",
  "Source Analytics",
  "Context Switches",
  "Transitions",
];

function App() {
  const [activePage, setActivePage] = useState("Overview");

  const [summary, setSummary] = useState(null);
  const [hourlyData, setHourlyData] = useState([]);
  const [developerData, setDeveloperData] = useState([]);
  const [sourceData, setSourceData] = useState([]);
  const [contextData, setContextData] = useState([]);
  const [teamTransitionData, setTeamTransitionData] = useState([]);
  const [developerTransitionData, setDeveloperTransitionData] =
    useState([]);

  const [selectedTeam, setSelectedTeam] = useState("All");
  const [selectedDeveloper, setSelectedDeveloper] = useState("All");

  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const endpoints = [
          "/api/v1/summary",
          "/api/v1/trends/hourly",
          "/api/v1/developers/activity",
          "/api/v1/sources/activity",
          "/api/v1/context-switches",
          "/api/v1/transitions/summary",
          "/api/v1/developers/transitions/summary",
        ];

        const responses = await Promise.all(
          endpoints.map((endpoint) => fetch(endpoint))
        );

        if (responses.some((response) => !response.ok)) {
          throw new Error("One or more analytics endpoints failed.");
        }

        const [
          summaryResult,
          hourlyResult,
          developerResult,
          sourceResult,
          contextResult,
          teamTransitionResult,
          developerTransitionResult,
        ] = await Promise.all(
          responses.map((response) => response.json())
        );

        setSummary(summaryResult);

        setHourlyData(
          hourlyResult.map((item) => ({
            hour: new Date(item.timestamp).toLocaleString([], {
              day: "2-digit",
              hour: "2-digit",
            }),
            event_count: item.event_count,
          }))
        );

        setDeveloperData(
          developerResult.map((developer) => {
            const counts = {};

            developer.events_by_source.forEach((item) => {
              counts[item.source] = item.count;
            });

            return {
              developer_id: developer.developer_id,
              team_id: developer.team_id,
              total_events: developer.total_events,
              github: counts.github || 0,
              ide: counts.ide || 0,
              jira: counts.jira || 0,
              slack: counts.slack || 0,
            };
          })
        );

        setSourceData(sourceResult);
        setContextData(contextResult);
        setTeamTransitionData(teamTransitionResult);
        setDeveloperTransitionData(developerTransitionResult);
        setApiError("");
      } catch (error) {
        setApiError(error.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  // Context-switch records grouped by developer.
  const developerSwitchData = useMemo(() => {
    const grouped = {};

    contextData.forEach((item) => {
      if (!grouped[item.developer_id]) {
        grouped[item.developer_id] = {
          developer_id: item.developer_id,
          short_gap: 0,
          long_gap: 0,
          total_transitions: 0,
        };
      }

      grouped[item.developer_id].total_transitions += 1;

      if (item.gap_seconds <= 1800) {
        grouped[item.developer_id].short_gap += 1;
      } else {
        grouped[item.developer_id].long_gap += 1;
      }
    });

    return Object.values(grouped).sort((a, b) =>
      a.developer_id.localeCompare(b.developer_id)
    );
  }, [contextData]);

  // Source-to-source transition patterns.
  const transitionPatterns = useMemo(() => {
    const grouped = {};

    contextData.forEach((item) => {
      const label = `${item.previous_source} → ${item.current_source}`;
      grouped[label] = (grouped[label] || 0) + 1;
    });

    return Object.entries(grouped)
      .map(([transition, count]) => ({ transition, count }))
      .sort((a, b) => b.count - a.count);
  }, [contextData]);

  // Team transition patterns for the chart.
  const teamTransitionChartData = useMemo(() => {
    return teamTransitionData
      .filter(
        (item) =>
          selectedTeam === "All" || item.team_id === selectedTeam
      )
      .map((item) => ({
        transition: `${item.previous_source} → ${item.current_source}`,
        team_id: item.team_id,
        total_transitions: item.total_transitions,
        short_gap_transitions: item.short_gap_transitions,
        long_gap_transitions: item.long_gap_transitions,
      }))
      .sort((a, b) => b.total_transitions - a.total_transitions);
  }, [teamTransitionData, selectedTeam]);

  // Developer transition summaries filtered by team and developer.
  const filteredDeveloperTransitions = useMemo(() => {
    return developerTransitionData.filter((item) => {
      const matchesTeam =
        selectedTeam === "All" || item.team_id === selectedTeam;

      const matchesDeveloper =
        selectedDeveloper === "All" ||
        item.developer_id === selectedDeveloper;

      return matchesTeam && matchesDeveloper;
    });
  }, [developerTransitionData, selectedTeam, selectedDeveloper]);

  // Team transition table filtered by selected team.
  const filteredTeamTransitions = useMemo(() => {
    return teamTransitionData.filter(
      (item) =>
        selectedTeam === "All" || item.team_id === selectedTeam
    );
  }, [teamTransitionData, selectedTeam]);

  // Keep developer filter options relevant to the selected team.
  const availableDevelopers = useMemo(() => {
    return developerTransitionData
      .filter(
        (item) =>
          selectedTeam === "All" || item.team_id === selectedTeam
      )
      .map((item) => item.developer_id)
      .sort();
  }, [developerTransitionData, selectedTeam]);

  // Filter the recent event-level transitions.
  const filteredContextData = useMemo(() => {
    return contextData.filter((item) => {
      const developer = developerData.find(
        (person) => person.developer_id === item.developer_id
      );

      const matchesTeam =
        selectedTeam === "All" ||
        developer?.team_id === selectedTeam;

      const matchesDeveloper =
        selectedDeveloper === "All" ||
        item.developer_id === selectedDeveloper;

      return matchesTeam && matchesDeveloper;
    });
  }, [contextData, developerData, selectedTeam, selectedDeveloper]);

  const shortGapCount = contextData.filter(
    (item) => item.gap_seconds <= 1800
  ).length;

  const longGapCount = contextData.length - shortGapCount;

  const filteredTotalTransitions = filteredDeveloperTransitions.reduce(
    (sum, item) => sum + item.total_transitions,
    0
  );

  const filteredShortTransitions = filteredDeveloperTransitions.reduce(
    (sum, item) => sum + item.short_gap_transitions,
    0
  );

  const filteredLongTransitions = filteredDeveloperTransitions.reduce(
    (sum, item) => sum + item.long_gap_transitions,
    0
  );

  const formatTimestamp = (value) => {
    if (!value) return "—";

    return new Date(value).toLocaleString([], {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatGap = (seconds) => {
    if (seconds < 60) return `${seconds}s`;

    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    }

    return `${minutes}m`;
  };

  const metrics = [
    {
      title: "Total Events",
      value: summary?.total_events ?? "—",
      description: "Recorded workflow events",
    },
    {
      title: "Active Developers",
      value: summary?.unique_developers ?? "—",
      description: "Developers represented",
    },
    {
      title: "Connected Sources",
      value: summary?.events_by_source?.length ?? "—",
      description: "Integrated platforms",
    },
    {
      title: "Teams",
      value: summary?.unique_teams ?? "—",
      description: "Teams represented",
    },
  ];

  const contextMetrics = [
    {
      title: "Total Transitions",
      value: contextData.length,
      description: "Recorded source changes",
    },
    {
      title: "Shorter Gaps",
      value: shortGapCount,
      description: "Up to 30 minutes",
    },
    {
      title: "Longer Gaps",
      value: longGapCount,
      description: "Over 30 minutes",
    },
    {
      title: "Developers",
      value: developerSwitchData.length,
      description: "With recorded transitions",
    },
  ];

  const transitionMetrics = [
    {
      title: "Filtered Transitions",
      value: filteredTotalTransitions,
      description: "For current selection",
    },
    {
      title: "Shorter Gaps",
      value: filteredShortTransitions,
      description: "Up to 30 minutes",
    },
    {
      title: "Longer Gaps",
      value: filteredLongTransitions,
      description: "Over 30 minutes",
    },
    {
      title: "Developers",
      value: filteredDeveloperTransitions.length,
      description: "In current selection",
    },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen">

        {/* Sidebar */}
        <aside className="hidden w-64 shrink-0 flex-col border-r border-slate-200 bg-white md:flex">
          <div className="border-b border-slate-200 px-6 py-6">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-xl font-bold text-white">
                C
              </div>
              <div>
                <h1 className="text-lg font-bold">CogniStream</h1>
                <p className="text-xs text-slate-500">
                  Developer Analytics
                </p>
              </div>
            </div>
          </div>

          <nav className="space-y-1 px-4 py-6">
            <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
              Workspace
            </p>

            {navigation.map((item) => (
              <button
                key={item}
                onClick={() => setActivePage(item)}
                className={`w-full rounded-lg px-3 py-3 text-left text-sm font-medium transition ${
                  activePage === item
                    ? "bg-blue-50 text-blue-700"
                    : "text-slate-600 hover:bg-slate-100"
                }`}
              >
                {item}
              </button>
            ))}
          </nav>

          <div className="mt-auto border-t border-slate-200 p-5">
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-sm font-semibold">Data Pipeline</p>
              <p className="mt-2 text-xs text-slate-500">
                Demo environment
              </p>
            </div>
          </div>
        </aside>

        {/* Main area */}
        <main className="min-w-0 flex-1">
          <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-5 lg:px-10">
            <div>
              <p className="text-sm text-slate-500">
                Workspace / Analytics
              </p>
              <h2 className="mt-1 text-xl font-bold">{activePage}</h2>
            </div>
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-sm font-bold text-blue-700">
              CS
            </div>
          </header>

          <div className="mx-auto max-w-7xl space-y-8 px-6 py-8 lg:px-10">

            {loading && (
              <p className="text-sm text-slate-500">
                Loading dashboard analytics...
              </p>
            )}

            {apiError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                Unable to load analytics: {apiError}
              </div>
            )}

            {/* Overview KPIs */}
            <section>
              <div className="mb-6">
                <Title>Developer Activity Overview</Title>
                <Text>
                  Monitor developer workflow events and activity patterns
                  across connected sources.
                </Text>
              </div>

              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
                {metrics.map((item) => (
                  <Card key={item.title}>
                    <Text>{item.title}</Text>
                    <Metric className="mt-3">{item.value}</Metric>
                    <Text className="mt-2">{item.description}</Text>
                  </Card>
                ))}
              </div>
            </section>

            {/* Hourly Activity and Sources */}
            <section className="grid grid-cols-1 gap-5 xl:grid-cols-3">
              <Card className="xl:col-span-2">
                <Title>Hourly Activity Trends</Title>
                <Text>
                  Developer workflow events recorded per hour.
                </Text>

                <div className="mt-6">
                  <AreaChart
                    className="h-72"
                    data={hourlyData}
                    index="hour"
                    categories={["event_count"]}
                    colors={["blue"]}
                    showLegend={false}
                    showGridLines
                    curveType="monotone"
                    yAxisWidth={45}
                  />
                </div>
              </Card>

              <Card>
                <Title>Event Sources</Title>
                <Text>Connected data sources</Text>

                <div className="mt-6 space-y-5">
                  {(summary?.events_by_source || []).map((item) => {
                    const percentage = summary.total_events
                      ? (item.count / summary.total_events) * 100
                      : 0;

                    return (
                      <div key={item.source}>
                        <div className="mb-2 flex justify-between text-sm">
                          <span className="font-medium capitalize">
                            {item.source}
                          </span>
                          <span className="text-slate-500">
                            {item.count} events
                          </span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                          <div
                            className={`h-full rounded-full ${
                              sourceColors[item.source] || "bg-blue-500"
                            }`}
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </Card>
            </section>

            {/* Developer Activity */}
            <section>
              <Card>
                <Title>Developer Activity Comparison</Title>
                <Text>
                  Compare event activity across developers and connected sources.
                </Text>

                <div className="mt-6">
                  <BarChart
                    className="h-80"
                    data={developerData}
                    index="developer_id"
                    categories={["github", "ide", "jira", "slack"]}
                    colors={["slate", "emerald", "blue", "violet"]}
                    showLegend
                    showGridLines
                    yAxisWidth={45}
                  />
                </div>

                <div className="mt-6 border-t border-slate-200 pt-5">
                  <Title>Developer Summary</Title>
                  <div className="mt-4 overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead>
                        <tr className="border-b text-slate-500">
                          <th className="px-3 py-3">Developer</th>
                          <th className="px-3 py-3">Team</th>
                          <th className="px-3 py-3 text-right">
                            Total Events
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {developerData.map((developer) => (
                          <tr
                            key={developer.developer_id}
                            className="border-b border-slate-100"
                          >
                            <td className="px-3 py-3 font-medium">
                              {developer.developer_id}
                            </td>
                            <td className="px-3 py-3">
                              {developer.team_id}
                            </td>
                            <td className="px-3 py-3 text-right font-semibold">
                              {developer.total_events}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>
            </section>

            {/* Source Activity */}
            <section>
              <div className="mb-5">
                <Title>Source Activity Analytics</Title>
                <Text>
                  Event volume, developer coverage, and activity windows.
                </Text>
              </div>

              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
                {sourceData.map((source) => (
                  <Card key={source.source}>
                    <div className="flex justify-between">
                      <Text className="capitalize">{source.source}</Text>
                      <span
                        className={`h-3 w-3 rounded-full ${
                          sourceColors[source.source] || "bg-blue-500"
                        }`}
                      />
                    </div>
                    <Metric className="mt-3">
                      {source.total_events}
                    </Metric>
                    <Text>Recorded events</Text>

                    <div className="mt-5 border-t border-slate-100 pt-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-500">
                          Active developers
                        </span>
                        <span className="font-semibold">
                          {source.active_developers}
                        </span>
                      </div>
                      <p className="mt-4 text-xs font-semibold uppercase text-slate-400">
                        First event
                      </p>
                      <p className="mt-1 text-sm">
                        {formatTimestamp(source.first_event)}
                      </p>
                      <p className="mt-4 text-xs font-semibold uppercase text-slate-400">
                        Last event
                      </p>
                      <p className="mt-1 text-sm">
                        {formatTimestamp(source.last_event)}
                      </p>
                    </div>
                  </Card>
                ))}
              </div>
            </section>

            {/* Context Switch Analytics */}
            <section>
              <div className="mb-6">
                <Title>Context-Switch Analytics</Title>
                <Text>
                  Explore changes between event sources and the time gaps
                  between consecutive recorded events.
                </Text>
              </div>

              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
                {contextMetrics.map((item) => (
                  <Card key={item.title}>
                    <Text>{item.title}</Text>
                    <Metric className="mt-3">{item.value}</Metric>
                    <Text className="mt-2">{item.description}</Text>
                  </Card>
                ))}
              </div>

              <div className="mt-5 grid grid-cols-1 gap-5 xl:grid-cols-2">
                <Card>
                  <Title>Transition Gaps by Developer</Title>
                  <Text>
                    Comparison of gaps up to and over 30 minutes.
                  </Text>

                  <div className="mt-6">
                    <BarChart
                      className="h-72"
                      data={developerSwitchData}
                      index="developer_id"
                      categories={["short_gap", "long_gap"]}
                      colors={["emerald", "violet"]}
                      showLegend
                      showGridLines
                      yAxisWidth={40}
                    />
                  </div>
                </Card>

                <Card>
                  <Title>Source Transition Patterns</Title>
                  <Text>
                    Most frequently observed source-to-source transitions.
                  </Text>

                  <div className="mt-6">
                    <BarChart
                      className="h-72"
                      data={transitionPatterns}
                      index="transition"
                      categories={["count"]}
                      colors={["blue"]}
                      showLegend={false}
                      showGridLines
                      yAxisWidth={40}
                    />
                  </div>
                </Card>
              </div>

              <Card className="mt-5">
                <Title>Recent Source Transitions</Title>
                <Text>
                  Recorded source changes with their event timestamps and gaps.
                </Text>

                <div className="mt-5 overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500">
                        <th className="px-3 py-3">Developer</th>
                        <th className="px-3 py-3">From</th>
                        <th className="px-3 py-3">To</th>
                        <th className="px-3 py-3">Previous Event</th>
                        <th className="px-3 py-3">Current Event</th>
                        <th className="px-3 py-3 text-right">Gap</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[...contextData]
                        .sort(
                          (a, b) =>
                            new Date(b.current_timestamp) -
                            new Date(a.current_timestamp)
                        )
                        .slice(0, 10)
                        .map((item, index) => (
                          <tr
                            key={`${item.developer_id}-${item.current_timestamp}-${index}`}
                            className="border-b border-slate-100"
                          >
                            <td className="px-3 py-3 font-medium">
                              {item.developer_id}
                            </td>
                            <td className="px-3 py-3 capitalize">
                              {item.previous_source}
                            </td>
                            <td className="px-3 py-3 capitalize">
                              {item.current_source}
                            </td>
                            <td className="px-3 py-3 whitespace-nowrap">
                              {formatTimestamp(item.previous_timestamp)}
                            </td>
                            <td className="px-3 py-3 whitespace-nowrap">
                              {formatTimestamp(item.current_timestamp)}
                            </td>
                            <td className="px-3 py-3 text-right font-medium">
                              {formatGap(item.gap_seconds)}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </section>

            {/* Transition Summary Analytics */}
            <section>
              <div className="mb-6">
                <Title>Transition Summary Analytics</Title>
                <Text>
                  Compare aggregated source transitions across teams and developers.
                </Text>
              </div>

              {/* Filters */}
              <Card>
                <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                  <div>
                    <label
                      htmlFor="team-filter"
                      className="mb-2 block text-sm font-medium text-slate-700"
                    >
                      Filter by Team
                    </label>
                    <select
                      id="team-filter"
                      value={selectedTeam}
                      onChange={(event) => {
                        setSelectedTeam(event.target.value);
                        setSelectedDeveloper("All");
                      }}
                      className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
                    >
                      <option value="All">All Teams</option>
                      {[...new Set(
                        teamTransitionData.map((item) => item.team_id)
                      )]
                        .sort()
                        .map((team) => (
                          <option key={team} value={team}>
                            {team}
                          </option>
                        ))}
                    </select>
                  </div>

                  <div>
                    <label
                      htmlFor="developer-filter"
                      className="mb-2 block text-sm font-medium text-slate-700"
                    >
                      Filter by Developer
                    </label>
                    <select
                      id="developer-filter"
                      value={selectedDeveloper}
                      onChange={(event) =>
                        setSelectedDeveloper(event.target.value)
                      }
                      className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
                    >
                      <option value="All">All Developers</option>
                      {availableDevelopers.map((developer) => (
                        <option key={developer} value={developer}>
                          {developer}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </Card>

              {/* Filtered KPIs */}
              <div className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
                {transitionMetrics.map((item) => (
                  <Card key={item.title}>
                    <Text>{item.title}</Text>
                    <Metric className="mt-3">{item.value}</Metric>
                    <Text className="mt-2">{item.description}</Text>
                  </Card>
                ))}
              </div>

              {/* Developer Transition Comparison */}
              <Card className="mt-5">
                <Title>Developer Transition Comparison</Title>
                <Text>
                  Total transitions and gap categories by developer.
                </Text>

                <div className="mt-6">
                  <BarChart
                    className="h-80"
                    data={filteredDeveloperTransitions}
                    index="developer_id"
                    categories={[
                      "short_gap_transitions",
                      "long_gap_transitions",
                    ]}
                    colors={["emerald", "violet"]}
                    showLegend
                    showGridLines
                    yAxisWidth={45}
                  />
                </div>

                <div className="mt-5 overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500">
                        <th className="px-3 py-3">Developer</th>
                        <th className="px-3 py-3">Team</th>
                        <th className="px-3 py-3 text-right">Transitions</th>
                        <th className="px-3 py-3 text-right">Short Gaps</th>
                        <th className="px-3 py-3 text-right">Long Gaps</th>
                        <th className="px-3 py-3 text-right">Avg Gap</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredDeveloperTransitions.map((item) => (
                        <tr
                          key={item.developer_id}
                          className="border-b border-slate-100"
                        >
                          <td className="px-3 py-3 font-medium">
                            {item.developer_id}
                          </td>
                          <td className="px-3 py-3">{item.team_id}</td>
                          <td className="px-3 py-3 text-right font-semibold">
                            {item.total_transitions}
                          </td>
                          <td className="px-3 py-3 text-right">
                            {item.short_gap_transitions}
                          </td>
                          <td className="px-3 py-3 text-right">
                            {item.long_gap_transitions}
                          </td>
                          <td className="px-3 py-3 text-right">
                            {formatGap(item.avg_gap_seconds)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>

              {/* Team Transition Patterns */}
              <Card className="mt-5">
                <Title>Team Source Transition Patterns</Title>
                <Text>
                  Frequency of source-to-source transitions grouped by team.
                </Text>

                <div className="mt-6">
                  <BarChart
                    className="h-80"
                    data={teamTransitionChartData}
                    index="transition"
                    categories={["total_transitions"]}
                    colors={["blue"]}
                    showLegend={false}
                    showGridLines
                    yAxisWidth={45}
                  />
                </div>

                <div className="mt-5 overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500">
                        <th className="px-3 py-3">Team</th>
                        <th className="px-3 py-3">From</th>
                        <th className="px-3 py-3">To</th>
                        <th className="px-3 py-3 text-right">Total</th>
                        <th className="px-3 py-3 text-right">Short Gaps</th>
                        <th className="px-3 py-3 text-right">Long Gaps</th>
                        <th className="px-3 py-3 text-right">Avg Gap</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredTeamTransitions.map((item, index) => (
                        <tr
                          key={`${item.team_id}-${item.previous_source}-${item.current_source}-${index}`}
                          className="border-b border-slate-100"
                        >
                          <td className="px-3 py-3 font-medium">
                            {item.team_id}
                          </td>
                          <td className="px-3 py-3 capitalize">
                            {item.previous_source}
                          </td>
                          <td className="px-3 py-3 capitalize">
                            {item.current_source}
                          </td>
                          <td className="px-3 py-3 text-right font-semibold">
                            {item.total_transitions}
                          </td>
                          <td className="px-3 py-3 text-right">
                            {item.short_gap_transitions}
                          </td>
                          <td className="px-3 py-3 text-right">
                            {item.long_gap_transitions}
                          </td>
                          <td className="px-3 py-3 text-right">
                            {formatGap(item.avg_gap_seconds)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>

              <p className="mt-3 text-xs leading-5 text-slate-500">
                Gap categories use a 30-minute threshold. They describe
                elapsed time between recorded events and should not be
                interpreted as direct measurements of interruption,
                recovery, cognitive load, or productivity.
              </p>
            </section>

            {/* Footer */}
            <footer className="border-t border-slate-200 pt-5 text-center text-xs text-slate-400">
              CogniStream · Developer Flow-State & Cognitive Load Analytics
              <p className="mt-1">
                Workflow activity indicators are analytical proxies, not
                direct measurements of cognitive state or productivity.
              </p>
            </footer>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
