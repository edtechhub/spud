# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2020-08-31

### Added

- Semantic value column added representing keywords contained in tak.
- HDI filters functionality for sorting GC filters.
- Highlighting for user searches.

### Changed

- Visual changes to UI displayed
- Resized displayed tables
- Rank was normalized (divided by length of tak)

## [1.1.b] - 2020-08-09

### Changed

- Fixed filtering by year on RIS export.
- Search engine checkbox stays ticked.

## [1.1.0] - 2020-07-27

### Added

- Searching by minimum year and maximum year functionality.
- Google analytics tracking code.
- Google cloud profiler for tracking CPU usage in processes.


### Changed

- New colours for the highlighting.
- All highlighted text is now black.
- HDI filter hidden until new functionality is done.
- Old search type fixed

## [1.0.b] - 2020-07-19

### Added

- Live timer for search queries.
- Jump to top button.
- This changelog file.
- Footer displaying version and copyright.

### Changed

- RIS export now includes all search results.
- URL is now shortened and allows more filters applied.
- Default address doesn't trigger any database searches.

## Initial release [1.0.0] - 2020-07-09

### Added

- Full text search functionality for both tak and query fields.
- Min-HDI and Max-HDI filters for querying through the GC filter.
- 7 filters for optimized search experience.
- Old search type for backwards functionality.
- "Include rank < 10" button to show less relevant results.
- Calculated relevance score for each record.
- New column rank that displays computed relevance.

### Changed

- Sorting by rank instead of year.
