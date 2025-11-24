# MCP Server Dashboard and Configuration View

## Overview

The MCP (Model Context Protocol) Server Dashboard provides a comprehensive view of configured MCP servers with expandable details showing their configuration, status, and metadata. This enhancement makes it easier to manage and troubleshoot MCP server integrations.

## Features

### Server Card Display

Each MCP server is displayed in an expandable card format with:

#### Summary View (Default)
- **Server Name**: Display name of the MCP server
- **Type**: Connection type (stdio, http)
- **Status Indicator**: Visual indicator showing if the server is active or inactive
  - ● Green bullet = Active
  - ○ Gray bullet = Inactive
- **Expand/Collapse Button**: Chevron icon to show/hide detailed information

#### Detailed View (Expanded)

When expanded, each server card shows:

##### Command Information
```bash
npx
```
The executable command used to start the MCP server.

##### Arguments
```json
[
  "-y",
  "@modelcontextprotocol/server-sequential-thinking"
]
```
Command-line arguments passed to the server.

##### Environment Variables
```json
{
  "API_KEY": "your-key",
  "DEBUG": "true"
}
```
Environment variables set for the server process.

##### URL (for HTTP servers)
```
http://localhost:8080/mcp
```
The HTTP endpoint URL for HTTP-type servers.

##### Timestamps
- **Created**: When the server configuration was created
- **Updated**: Last time the server configuration was modified

## User Interface

### Layout

The MCP Tools & Servers page is organized into sections:

1. **Header Bar**
   - Page title: "MCP Tools & Servers"
   - Action buttons:
     - Export Servers
     - Import Servers
     - Add Server
     - Refresh

2. **MCP Servers Section**
   - Displays all configured servers
   - Single-column layout for better detail visibility
   - Each server in an expandable card

3. **Available Tools Section**
   - Lists all tools available from active MCP servers
   - Searchable by tool name, description, or server
   - Shows tool parameters and descriptions

### Server Card Interactions

#### Expanding/Collapsing Details

- Click the chevron icon (↓/↑) next to the server name to toggle details
- Multiple servers can be expanded simultaneously
- Expansion state is maintained during the session

#### Server Actions

Each server card has action buttons:

- **Edit** (pencil icon): Modify server configuration
- **Delete** (trash icon): Remove the server

## Implementation Details

### Backend Changes

No backend changes were required. The existing MCP server API endpoints provide all necessary data:

- `GET /api/mcp-servers`: Lists all servers with full configuration
- `GET /api/mcp-servers/{id}`: Gets specific server details
- `POST /api/mcp-servers`: Creates a new server
- `PUT /api/mcp-servers/{id}`: Updates server configuration
- `DELETE /api/mcp-servers/{id}`: Deletes a server

### Frontend Changes

#### MCPToolsPage Component

New state management:
```typescript
const [expandedServers, setExpandedServers] = useState<Set<number>>(new Set())
```

New functions:
```typescript
const toggleServerExpanded = (serverId: number) => {
  // Toggles expansion state for a server
}
```

Updated UI components:
- Chevron icons for expand/collapse
- Conditional rendering of detailed information
- Improved status indicators
- Better layout for configuration data

## Usage Guide

### Viewing Server Details

1. Navigate to the "MCP Tools & Servers" page
2. Locate the server you want to inspect
3. Click the chevron (↓) icon next to the server name
4. The card expands to show all configuration details
5. Click the chevron (↑) again to collapse the details

### Managing Servers

#### Adding a Server

1. Click the "Add Server" button
2. Fill in the server configuration:
   - Name: Unique identifier
   - Command: Executable path or command
   - Arguments: JSON array of command arguments
   - Environment: JSON object of environment variables
   - Type: stdio or http
   - URL: (Required for http type)
   - Active: Toggle to enable/disable the server

#### Editing a Server

1. Expand or locate the server card
2. Click the edit (pencil) icon
3. Modify the configuration fields
4. Click "Update" to save changes

#### Deleting a Server

1. Locate the server card
2. Click the delete (trash) icon
3. Confirm the deletion

### Importing/Exporting Servers

#### Export Servers

1. Click "Export Servers" button
2. All servers are exported to a JSON file (mcp.json format)
3. File is downloaded to your browser's download location

#### Import Servers

1. Click "Import Servers" button
2. Select an mcp.json format file
3. Servers from the file are added to the configuration
4. Duplicate server names are skipped

## Configuration File Format

The import/export feature uses the standard mcp.json format:

```json
{
  "servers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "type": "stdio",
      "env": {
        "API_KEY": "your-key"
      }
    },
    "http-example": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "type": "http",
      "url": "http://localhost:8080/mcp"
    }
  },
  "inputs": []
}
```

## Benefits

1. **Better Visibility**: See all server configuration at a glance
2. **Easier Debugging**: Quickly inspect command, args, and environment
3. **Configuration Management**: Export/import server configurations
4. **Status Monitoring**: Visual indicators show server status
5. **Space Efficient**: Collapsed by default, expand only when needed

## Use Cases

### Development and Testing

- Verify server configurations are correct
- Check environment variables are properly set
- Confirm command paths and arguments

### Troubleshooting

- Review server settings when connections fail
- Compare working and non-working server configurations
- Identify missing environment variables or incorrect URLs

### Configuration Migration

- Export server configurations from one environment
- Import into another environment
- Share standard server configurations with team members

## Future Enhancements

Potential improvements for future versions:

- Real-time connection status checking
- Server health monitoring
- Performance metrics
- Tool usage statistics per server
- Connection test functionality
- Server logs viewing
- Automatic server discovery
- Configuration validation
- Template-based server creation
