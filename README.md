# star-net
### Self organizing hub and spoke network with chat functionality.

Star-net is a reliable message broadcasting system over a secure self-organizing network. In summary, nodes monitor the network to see what other nodes are online then calculate which node has the shortest sum round trip time to all other nodes which, once calculated, gets set as the central hub node. Any node that wants to send a message does so by sending it to the hub node, which broadcasts it to all other nodes via a hub-and-spoke star network. Each node continuously interacts with all other nodes to determine an optimal network formation. Although the network operates on a custom UDP sockets, the reliability of message broadcasting is still guaranteed through acknowledgments that work in real-time.

Star-net also has built in summarization capabliities.  The conversations of groups are logged and then summaried for a new user when they enter the chat.

### How to run star-net
In your terminal navigate to the file named starNet_textSum.py which will be in the folder star-net.  The format of the input is python3 starNet_textSum.py <chatname> <your port number> <friend's port number> <number of nodes in network>.  So for example an input could look like python3 starNet_textSum.py laddjones 4000 4001 4.  This would mean that I am expecting 4 other to be online with me.
