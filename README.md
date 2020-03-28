# star-net
Self organizing hub and spoke network with chat functionality.

Star-net is a reliable message broadcasting system over a secure self-organizing network. In summary, nodes monitor the network to see what other nodes are online then calculate which node has the shortest sum round trip time to all other nodes which, once calculated, gets set as the central hub node. Any node that wants to send a message does so by sending it to the hub node, which broadcasts it to all other nodes via a hub-and-spoke star network. Each node continuously interacts with all other nodes to determine an optimal network formation. Although the network operates on a custom UDP sockets, the reliability of message broadcasting is still guaranteed through acknowledgments that work in real-time.

Star-net also has built in summarization capabliities.  The conversations of groups are logged and then summaried for a new user when they enter the chat.
